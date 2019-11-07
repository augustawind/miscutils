"""namespaced constants

A :class:`Const` is a fixed set of names bound to fixed values (constants). It
allows you to turn code like this:

.. code-block:: python

    IS_COOL = True
    FOO_BAR_BAZ = 3
    API_URL = "bananas.io/v2"

into code like this:

.. code-block:: python

    from miscutils.const import Const

    class Settings(Const):
        IS_COOL = True
        FOO_BAR_BAZ = 3
        API_URL = "bananas.io/v2"

In cases where the value doesn't matter, you can leave it out and a default
will be generated based on the name:

>>> class Color(Const):
...     RED: str
...     YELLOW: str
...     BLUE: str
>>> Color.YELLOW
'yellow'

You can customize how default values are generated with the ``default_factory``
class attribute. It should be a callable that takes the name of the constant
value and returns the generated value:

>>> class Color(Const):
...     default_factory = str.title
...     RED: str
>>> Color.RED
'Red'

By default, values are generated with ``str.lower``.

Const is immutable: it's attributes cannot be changed or deleted, and new
attributes cannot be added to it once it is defined. Attempting to set or
delete an attribute on a Const will raise a :class:`ConstError`.
"""
from types import MappingProxyType
from typing import Any, Mapping

__all__ = ["Const", "ConstError", "ConstMeta"]


class ConstError(TypeError):
    """Error raised when attempting to set or delete values of a Const."""


class ConstMeta(type):
    """Metaclass for Const.

    The following declarations are equivalent:

    >>> class Foo(metaclass=ConstMeta): pass
    >>> class Foo(Const): pass
    """

    def __new__(cls, name, bases, ns):
        # Extract defined constants
        members = {
            key: val
            for key, val in ns.items()
            if key != "default_factory" and not key.startswith("__")
        }
        for key in members:
            del ns[key]

        # Generate values for constants that are only named (e.g. FOO: str)
        types = ns.get("__annotations__", {})
        factory = ns.pop("default_factory", str.lower)
        for field_name in types:
            if field_name not in members:
                members[field_name] = factory(field_name)

        ns["_member_map_"] = members

        return super().__new__(cls, name, bases, ns)

    def __getitem__(cls, item):
        return cls._member_map_[item]

    def __getattr__(cls, attr):
        try:
            return cls._member_map_[attr]
        except KeyError as exc:
            raise AttributeError(*exc.args)

    def __setattr__(cls, attr, value):
        raise ConstError(
            "'Const' object does not support attribute assignment"
        )

    def __delattr__(cls, attr):
        raise ConstError("'Const' object does not support attribute deletion")

    def __iter__(cls):
        return iter(cls._member_map_.values())

    def __len__(cls):
        return len(cls._member_map_)

    @property
    def __members__(cls) -> Mapping[str, Any]:
        """A read-only ordered mapping of names to members."""
        return MappingProxyType(cls._member_map_)


class Const(metaclass=ConstMeta):
    """Immutable container for fixed values.

    Derive from this class to define a group of constants. See module docs for
    examples.
    """
