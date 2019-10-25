"""views - mutable slices of compound data types"""
from collections.abc import Iterable, Mapping, MutableMapping


class DictView(MutableMapping):
    """A DictView is a mutable reference to a subset of a Mapping's keys."""
    def __init__(self, obj: MutableMapping, keys: Iterable):
        self.__obj = obj
        self.__keys = set(keys)

    def __iter__(self):
        for key in self.__keys:
            if key in self.__obj:
                yield key
            else:
                self.__keys.remove(key)

    def __len__(self):
        return len(tuple(iter(self)))

    def __getitem__(self, key):
        if key not in self.__keys:
            raise KeyError(key)
        return self.__obj[key]

    def __setitem__(self, key, value):
        if key not in self.__keys:
            raise KeyError(key)
        self.__obj[key] = value

    def __delitem__(self, key):
        if key not in self.__keys:
            raise KeyError(key)
        del self.__obj[key]
        self.__keys.remove(key)

    def keys(self):
        return iter(self)

    def values(self):
        for key in self:
            yield self.__obj[key]

    def items(self):
        for key in self:
            yield (key, self.__obj[key])

    def __eq__(self, other):
        return isinstance(other, Mapping) and dict(self.items()) == dict(
            other.items()
        )
