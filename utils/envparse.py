import os
from collections import OrderedDict
from typing import Any
import argparse

from utils.mappings import Namespace


class Error(Exception):
    """Base Exception type for the ``envparse`` module."""

    def _fmt(self, msg):
        return f'error: {msg}'


class InvalidParam(Error):
    """Invalid ``Param`` instantiation."""

    def __init__(self, msg):
        self.path = None
        self.msg = msg

    def __str__(self):
        return self._fmt(f'invalid param defined at {self.path}: {self.msg}')


class ParseError(Error):
    """A parameter was not satisfied."""

    def __init__(self, param):
        self.param = param


class InvalidValue(ParseError):

    def __init__(self, param, value, expected):
        super().__init__(param)
        self.value = value
        self.expected = expected

    def __str__(self):
        return self._fmt(
            f'invalid value for {self.param.envvar}:'
            f' expected {self.expected}, got {self.value}'
        )


class MissingValue(ParseError):

    def __str__(self):
        return self._fmt(f'{self.param.envvar} is required')


class DEFAULT:
    """Non-None default value."""


class Param:

    def __init__(self, type_: type=str, default: Any=DEFAULT,
                 required: bool=DEFAULT):
        self.type = type_
        self.default = default
        self.required = required

        self.name = None
        self.breadcrumbs = []
        self.prefix = None

    def _validate(self):
        # If there is no `default`, param MUST be required.
        if self.default is DEFAULT:
            self.default = None
            if self.required is False:
                raise InvalidParam('param must be have a default or be required')
            self.required = True
        # If there is a `default`, param MUST NOT be required.
        elif self.required is True:
            raise InvalidParam('cannot have a default and be required')
        else:
            self.required = False

    def register(self, name, prefix, breadcrumbs):
        try:
            self._validate()
        except InvalidParam as exc:
            exc.path = '.'.join((*breadcrumbs, name))
            raise

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
        if not src:
            if self.required:
                raise MissingValue(self)
            return self.default

        if self.type is bool:
            if src.lower() in ('1', 'true'):
                return True
            elif src.lower() in ('0', 'false'):
                return False
            raise InvalidValue(self, src, expected='bool')

        try:
            return self.type(src)
        except (TypeError, ValueError):
            raise InvalidValue(self, src, expected=self.type.__name__)


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

    def read(self, env=os.environ) -> Namespace:
        ns = Namespace()
        for name, param in self.params.items():
            print(f"name={name!r}")
            raw_value = env.get(param.envvar)
            print(f"param.envvar={param.envvar!r}")
            print(f"raw_value={raw_value!r}")
            value = param.read(raw_value)
            print(f"value={value!r}")
            print()
            for key in param.breadcrumbs:
                ns.setdefault(key, EnvSettings(key))
            ns[name] = value
        return ns
