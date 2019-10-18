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

    def __init__(self, param, msg):
        self.path = None
        self.param = param
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

    def _prepare(self):
        """Validate and prepare the ``Param`` for reading values."""
        # If there is no `default`, param MUST be required.
        if self.default is DEFAULT:
            self.default = None
            if self.required is False:
                raise InvalidParam(self, 'param must be have a default or be required')
            self.required = True
        # If there is a `default`, param MUST NOT be required.
        else:
            if self.required is True:
                raise InvalidParam(self, 'cannot have a default and be required')
            else:
                self.required = False

            # `default` must be an instance of `type`.
            if not isinstance(self.default, self.type):
                raise InvalidParam(
                    self,
                    f'param was defined with type {self.type.__name__}, but'
                    f' `default` has type {type(self.default).__name__}',
                )

    def register(self, name, prefix, breadcrumbs):
        try:
            self._prepare()
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

    def read(self, value: str) -> Any:
        if not value:
            if self.required:
                raise MissingValue(self)
            return self.default

        if self.type is bool:
            if value.lower() in ('1', 'true'):
                return True
            elif value.lower() in ('0', 'false'):
                return False
            raise InvalidValue(self, value, expected='bool')

        try:
            return self.type(value)
        except (TypeError, ValueError):
            raise InvalidValue(self, value, expected=self.type.__name__)


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
            raw_value = env.get(param.envvar)
            value = param.read(raw_value)
            for key in param.breadcrumbs:
                ns.setdefault(key, EnvSettings(key))
            ns[name] = value
        return ns
