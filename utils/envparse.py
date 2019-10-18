import os
from collections import OrderedDict
from typing import Any, Dict, List, Union

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

    def __init__(self, type_: type=str, *, default: Any=DEFAULT,
                 required: bool=DEFAULT):
        self.type = type_
        self.default = default
        self.required = required

        self.name = None
        self.breadcrumbs = []

    def _prepare(self):
        """Validate and prepare the ``Param`` for reading values."""
        # If there is no `default`, `required` defaults to True.
        if self.default is DEFAULT:
            self.default = None
            if self.required is DEFAULT:
                self.required = True
        # If there is a `default`, param MUST NOT be required.
        else:
            if self.required is True:
                raise InvalidParam(self, 'cannot have a default and be required')
            self.required = False

            # `default` must be an instance of `type`.
            if not isinstance(self.default, self.type):
                raise InvalidParam(
                    self,
                    f'param was defined with type {self.type.__name__}, but'
                    f' `default` has type {type(self.default).__name__}',
                )

    def register(self, name, breadcrumbs):
        try:
            self._prepare()
        except InvalidParam as exc:
            exc.path = '.'.join((*breadcrumbs, name))
            raise

        self.name = name
        self.breadcrumbs = breadcrumbs

        return self

    @property
    def envvar(self):
        return '_'.join((*self.breadcrumbs, self.name)).upper()

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


class EnvSettings:

    def __init__(self, **params):
        super().__init__()
        self.initial_params = params
        self.params = OrderedDict()

        self.name = None
        self.breadcrumbs = []

    def register(self, name: str, breadcrumbs: List[str]=None) -> 'EnvSettings':
        self.name = name
        self.breadcrumbs = [] if breadcrumbs is None else breadcrumbs

        for key, param in self.initial_params.items():
            param.register(key, breadcrumbs=[*self.breadcrumbs, self.name])
            self.params[key] = param

        return self

    def read(self, env=os.environ) -> Namespace:
        ns = Namespace()
        for name, param in self.params.items():
            if isinstance(param, EnvSettings):
                value = env
            else:
                value = env.get(param.envvar)
            ns[name] = param.read(value)
        return ns
