from collections.abc import Mapping


class ConstError(TypeError):
    pass


class ConstMeta(type):
    def __new__(cls, name, bases, ns):
        # Extract defined constants
        items = {
            key: val
            for key, val in ns.items()
            if key != "default_factory" and not key.startswith("__")
        }
        for key in items:
            del ns[key]

        # Generate values for constants that are only named (e.g. FOO: str)
        types = ns.get("__annotations__", {})
        factory = ns.pop("default_factory", str.lower)
        for field_name in types:
            if field_name not in items:
                items[field_name] = factory(field_name)

        ns["_items_"] = items

        return super().__new__(cls, name, bases, ns)

    def __getitem__(cls, item):
        return cls._items_[item]

    def __getattr__(cls, attr):
        return cls.__getitem__(attr)

    def __setattr__(cls, attr, value):
        raise ConstError("cannot rebind const value")

    def __delattr__(cls, attr):
        raise ConstError("cannot delete const value")

    def __iter__(cls):
        return iter(cls._items_)

    def __len__(cls):
        return len(cls._items_)

    def keys(cls):
        return tuple(cls._items_.keys())

    def values(cls):
        return tuple(cls._items_.values())

    def items(cls):
        return tuple(cls._items_.items())


class Const(metaclass=ConstMeta):
    pass
