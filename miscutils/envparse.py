from collections import OrderedDict
from typing import Any, Generic, Iterable, Mapping, Type, TypeVar, Union

from miscutils.mappings import Namespace


class Error(Exception):
    """Base Exception type for the ``envparse`` module."""

    def _fmt(self, msg: str) -> str:
        return f"error: {msg}"


class InvalidParam(Error):
    """Invalid ``Param`` instantiation."""

    def __init__(self, param: "Param", msg: str):
        self.path = None
        self.param = param
        self.msg = msg

    def __str__(self) -> str:
        return self._fmt(f"invalid param defined at {self.path}: {self.msg}")


class ParseError(Error):
    """A parameter was not satisfied while parsing."""

    def __init__(self, param: "Param"):
        self.param = param


class InvalidValue(ParseError):
    def __init__(self, param: "Param", value: Any, expected: Any):
        super().__init__(param)
        self.value = value
        self.expected = expected

    def __str__(self):
        return self._fmt(
            f"invalid value for {self.param.envvar}:"
            f" expected {self.expected}, got {self.value}"
        )


class MissingValue(ParseError):
    def __str__(self):
        return self._fmt(f"{self.param.envvar} is required")


class DEFAULT:
    """Non-None default value."""


Default = Type[DEFAULT]

T = TypeVar("ParamType", str, int, float, bool)


class Param(Generic[T]):
    def __init__(
        self,
        type_: Type[T] = str,
        *,
        default: Union[T, Default] = DEFAULT,
        required: Union[bool, Default] = DEFAULT,
    ):
        self.type = type_
        self.default = default
        self.required = required

        self.name = None
        self.breadcrumbs = []

    def _prepare(self):
        """Validates and prepares the Param for reading values."""
        # If there is no `default`, `required` defaults to True.
        if self.default is DEFAULT:
            self.default = None
            if self.required is DEFAULT:
                self.required = True
        # If there is a `default`, param MUST NOT be required.
        else:
            if self.required is True:
                raise InvalidParam(
                    self, "cannot have a default and be required"
                )
            self.required = False

            # `default` must be an instance of `type`.
            if not isinstance(self.default, self.type):
                raise InvalidParam(
                    self,
                    f"param was defined with type {self.type.__name__}, but"
                    f" `default` has type {type(self.default).__name__}",
                )

    def register(self, name: str, breadcrumbs: Iterable[str]) -> "Param[T]":
        """Registers the Param within the larger config structure.

        This method is called by the parent ``EnvParser`` to validate the
        parameter, contextualize it within the config structure, and get it
        into a ready state for parsing.

        Args:
            name: The parameter's key in the parent ``EnvParser``.
            breadcrumbs: A series of keys that locates the parameter from the
                top-level ``EnvParser``.

        Returns:
            self: This is just a convenience to allow method chaining.

        Raises:
            InvalidParam: If the Param is invalid.
        """
        try:
            self._prepare()
        except InvalidParam as exc:
            exc.path = ".".join((*breadcrumbs, name))
            raise

        self.name = name
        self.breadcrumbs = breadcrumbs

        return self

    @property
    def envvar(self) -> str:
        """Returns the environment variable that will be read by this Param."""
        return "_".join((*self.breadcrumbs, self.name)).upper()

    def read(self, env: Mapping[str, str]) -> T:
        """Attempts to read ``self.envvar`` from the given environment.

        Args:
            env: The environment to read from. Can be any mapping type.

        Returns:
            The result of reading and processing the environment variable.

        Raises:
            MissingValue: If there is no value (and the Param is required).
            InvalidValue: If the value exists but is invalid.
        """
        value = env.get(self.envvar)

        if not value:
            if self.required:
                raise MissingValue(self)
            return self.default

        if self.type is bool:
            if value.lower() in ("1", "true"):
                return True
            elif value.lower() in ("0", "false"):
                return False
            raise InvalidValue(self, value, expected="bool")

        try:
            return self.type(value)
        except (TypeError, ValueError):
            raise InvalidValue(self, value, expected=self.type.__name__)


class EnvParser:
    """A simple parser for keyed data.

    EnvParser parses flat data into nested structures. Parsers can be
    designed recursively in a nested map structure, where ``Param``s are the
    terminal nodes and ``EnvParser`` introduce another level of nesting.

    Example:
        >>> parser = EnvParser(
                name=Param(str),
                class=Param(str, default='monk'),
                skills=EnvParser(
                    meditation=Param(bool),
                    fighting=Param(bool),
                ),
            ).register('player')
        >>> env = dict(
                PLAYER_NAME='Foo',
                PLAYER_SKILLS_MEDITATION='true',
                PLAYER_SKILLS_FIGHTING='false',
            )
        >>> opts = parser.read(env)
        >>> print(opts.name)
        Foo
        >>> print(opts.skills.meditation)
        True
        >>> print(opts.skills.fighting)
        False
    """

    def __init__(self, **params: Union[Param, "EnvParser"]):
        super().__init__()
        self.initial_params = params
        self.params = OrderedDict()

        self.name = None
        self.breadcrumbs = []

    def register(
        self, name: str = None, breadcrumbs: Iterable[str] = None
    ) -> "EnvParser":
        self.breadcrumbs = [] if breadcrumbs is None else breadcrumbs

        if name:
            self.name = name
            breadcrumbs = [*self.breadcrumbs, name]
        else:
            breadcrumbs = list(self.breadcrumbs)

        for key, param in self.initial_params.items():
            param.register(key, breadcrumbs=breadcrumbs)
            self.params[key] = param

        return self

    def read(self, env: Mapping[str, str]) -> Namespace:
        ns = Namespace()
        for name, param in self.params.items():
            ns[name] = param.read(env)
        return ns
