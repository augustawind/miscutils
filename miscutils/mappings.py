from collections.abc import Iterable, Mapping, MutableMapping, Set

__all__ = [
    "DictSet",
    "FrozenDict",
    "FrozenDictSet",
    "FrozenNamespace",
    "Namespace",
]


class DictSet(MutableMapping, Set):
    """A dict that also functions as a set over its keys.

    DictSets are just like regular dictionaries but can also be treated as sets
    over their keys, and have access to modified versions of native set
    operations that function as closely as possible to a native set while still
    preserving the values associated with each key.

    This is not limited to operations between two DictSets. All of DictSet's
    set operations work with any Mapping type, and some work with Set types
    as well.

    When performing set operations between a DictSet and another Mapping type,
    if the returned DictSet contains keys that were in both operands, the
    values are taken from the leftmost Mapping.

    The `isdisjoint` and `intersection` operations work with any Iterable type.
    The `issubset`, `issuperset` and `difference` operations work with any
    Mapping or Set type. The `union` and `symmetric_difference` operations work
    with any Mapping type.
    """

    def __init__(self, *args, **kwargs):
        self.__dict = dict(*args, **kwargs)

    def __str__(self):
        return f"{self.__class__.__name__}({self.__dict})"

    __repr__ = __str__

    def update(self, *args, **kwargs):
        self.__dict.update(*args, **kwargs)

    def __contains__(self, item):
        return item in self.__dict

    def __iter__(self):
        return iter(self.__dict)

    def __len__(self):
        return len(self.__dict)

    def __getitem__(self, key):
        return self.__dict[key]

    def __setitem__(self, key, value):
        self.__dict[key] = value

    def __delitem__(self, key):
        del self.__dict[key]

    def __eq__(self, other):
        if not isinstance(other, Mapping):
            return NotImplemented
        return self.__dict == dict(other.items())

    def __le__(self, other):
        if not isinstance(other, (Mapping, Set)):
            return NotImplemented
        if len(self) > len(other):
            return False
        for elem in self:
            if elem not in other:
                return False
        return True

    def __ge__(self, other):
        if not isinstance(other, (Mapping, Set)):
            return NotImplemented
        if len(self) < len(other):
            return False
        for elem in other:
            if elem not in self:
                return False
        return True

    def __lt__(self, other):
        if not isinstance(other, (Mapping, Set)):
            return NotImplemented
        return len(self) < len(other) and self.__le__(other)

    def __gt__(self, other):
        if not isinstance(other, (Mapping, Set)):
            return NotImplemented
        return len(self) > len(other) and self.__ge__(other)

    def __or__(self, other):
        if not isinstance(other, Mapping):
            return NotImplemented
        return DictSet((k, v) for s in (self, other) for k, v in s.items())

    __ror__ = __or__

    def __and__(self, other):
        if not isinstance(other, Iterable):
            return NotImplemented
        return DictSet((k, self[k]) for k in other if k in self)

    __rand__ = __and__

    def __sub__(self, other):
        if not isinstance(other, (Mapping, Set)):
            if not isinstance(other, Iterable):
                return NotImplemented
            other = set(other)
        return DictSet((k, v) for k, v in self.items() if k not in other)

    def __rsub__(self, other):
        if not isinstance(other, Mapping):
            return NotImplemented
        return DictSet((k, v) for k, v in other.items() if k not in self)

    def __xor__(self, other):
        if not isinstance(other, Mapping):
            return NotImplemented
        return (self - other) | (other - self)

    __rxor__ = __xor__


class FrozenDict(Mapping):
    """A dict whose items cannot be modified."""

    def __init__(self, iterable=(), **kwargs):
        self.__dict = dict(iterable, **kwargs)

    def __str__(self):
        return f"{self.__class__.__name__}({self.__dict})"

    __repr__ = __str__

    def __getitem__(self, item):
        return self.__dict[item]

    def __iter__(self):
        return iter(self.__dict)

    def __len__(self):
        return len(self.__dict)


class FrozenDictSet(FrozenDict, Set):
    """A ``FrozenDict`` that also functions as a set over its keys."""


class Namespace(dict):
    """A dict that supports dot-access of its keys."""

    def __str__(self):
        return f"{self.__class__.__name__}({dict.__str__(self)})"

    __repr__ = __str__

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

    def __delattr__(self, attr):
        del self[attr]

    def __copy__(self):
        return Namespace(self)

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        self.clear()
        self.update(state)

    __deepcopy__ = None


class FrozenNamespace(FrozenDict):
    """A ``FrozenDict`` that supports dot-access of its keys."""

    def __getattr__(self, attr):
        return self[attr]
