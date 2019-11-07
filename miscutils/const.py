"""namespaced constants"""


class ConstError(TypeError):
    """Attempt to set or delete values of a Const."""


class ConstMeta(type):
    """Metaclass for Const."""

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

        ns["__members__"] = members

        return super().__new__(cls, name, bases, ns)

    def __getitem__(cls, item):
        return cls.__members__[item]

    def __getattr__(cls, attr):
        try:
            return cls.__getitem__(attr)
        except KeyError as exc:
            raise AttributeError(*exc.args)

    def __setattr__(cls, attr, value):
        raise ConstError("constants are read-only")

    def __delattr__(cls, attr):
        raise ConstError("constants are read-only")

    def __iter__(cls):
        return iter(cls.__members__)

    def __len__(cls):
        return len(cls.__members__)

    def keys(cls):
        return cls.__members__.keys()

    def values(cls):
        return cls.__members__.values()

    def items(cls):
        return cls.__members__.items()


class Const(metaclass=ConstMeta):
    """Immutable container for fixed values.

    Derive from this class to define a group of constants.
    """
