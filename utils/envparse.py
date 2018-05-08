import os
from typing import Any


class DEFAULT:
    """Non-None default value."""


class Param:

    def __init__(self, name: str, type_: type=str, default: Any=DEFAULT,
                 required=True):
        self.name = name
        self.type = type_
        if default is DEFAULT:
            self.default = None
            self.required = True
        else:
            self.default = default
            self.required = required

        self.breadcrumbs = []
        self.prefix = None

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

    def __init__(self, name: str, *params: Param):
        super().__init__()
        self.name = name
        self.params = []
        self.extend(*params, breadcrumbs=[])

    def extend(self, *params, breadcrumbs=None):
        if not breadcrumbs:
            breadcrumbs = []

        for p in params:
            if isinstance(p, EnvSettings):
                self.extend(*p.params, breadcrumbs=[*breadcrumbs, p.name])
                continue

            p.prefix = self.name
            p.breadcrumbs.extend(breadcrumbs)
            self.params.append(p)

    def __getattr__(self, attr):
        return self.__getitem__(attr)

    def __setattr__(self, key, val):
        return self.__setitem__(key, val)

    def read(self, env=os.environ):
        for param in self.params:
            src = env.get(param.envvar)
            val = param.read(src)
            settings = self
            for key in param.breadcrumbs:
                settings = settings.setdefault(key, EnvSettings(key))
            settings[param.name] = val
