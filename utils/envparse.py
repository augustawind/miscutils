import os
from collections import OrderedDict
from typing import Any


class DEFAULT:
    """Non-None default value."""


class Param:

    def __init__(self, type_: type=str, default: Any=DEFAULT,
                 required: bool=True):
        self.name = 'param'
        self.type = type_
        if default is DEFAULT:
            self.default = None
            self.required = True
        else:
            self.default = default
            self.required = required

        self.breadcrumbs = []
        self.prefix = None

    def register(self, name, prefix, breadcrumbs):
        self.name = name
        self.prefix = prefix
        self.breadcrumbs = breadcrumbs
        return self

    @property
    def envvar(self):
        prefix = ''
        if self.prefix:
            prefix = f'{self.prefix}_'
        if self.breadcrumbs:
            prefix += f"{'_'.join(self.breadcrumbs)}_"
        var = prefix + self.name
        return var.upper()

    def read(self, src: str) -> Any:
        if src is None:
            if self.required:
                raise Exception(f'{self.name}: required')
            return self.default
        try:
            if self.type is bool:
                if src.lower() in ('1', 'true'):
                    return True
                elif src.lower() in ('0', 'false'):
                    return False
                raise ValueError
            return self.type(src)
        except (TypeError, ValueError):
            raise Exception(f'{self.name}: expected a {self.type}, got {src}')


class EnvSettings(dict):

    def __init__(self, name: str=None, **params):
        super().__init__()
        self.name = name
        self.kwargs = params
        self.params = OrderedDict()

    def register(self, name):
        self.name = name
        self.extend(**self.kwargs)
        return self

    def extend(self, _breadcrumbs: list=None, **params):
        if _breadcrumbs is None:
            _breadcrumbs = []

        for name, p in params.items():
            if isinstance(p, EnvSettings):
                p.register(name)
                self.extend(_breadcrumbs=[*_breadcrumbs, name], **p.params)
                continue
            p.register(name, self.name, _breadcrumbs)
            p.prefix = self.name
            p.breadcrumbs.extend(_breadcrumbs)
            self.params[name] = p

    def __getattr__(self, attr):
        return self.__getitem__(attr)

    def __setattr__(self, key, val):
        return self.__setitem__(key, val)

    def read(self, env=os.environ):
        for name, param in self.params.items():
            print(name)
            src = env.get(param.envvar)
            print(param.envvar)
            print(src)
            val = param.read(src)
            print(val)
            settings = self
            print()
            for key in param.breadcrumbs:
                settings = settings.setdefault(key, EnvSettings(key))
            settings[name] = val
