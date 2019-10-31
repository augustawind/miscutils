"""views - mutable slices of compound data types"""
from collections.abc import Iterable, Mapping, MutableMapping, MutableSet, Set


class SetView(MutableSet):
    def __init__(self, obj: Iterable, values: Iterable):
        self.__obj = set(obj)
        self.__values = set(values)

    def _from_iterable(self, it):
        return SetView(it, self.__values)

    def __contains__(self, item):
        return item in self.__values

    def __iter__(self):
        for item in self.__values:
            if item in self.__obj:
                yield item
            else:
                self.__values.discard(item)

    def __len__(self):
        return len(tuple(iter(self)))

    def add(self, value):
        self.__obj.add(value)
        self.__values.add(value)

    def discard(self, value):
        if value in self.__values:
            self.__obj.discard(value)
            self.__values.remove(value)

    def clear(self):
        self.__obj -= self.__values
        self.__values.clear()


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
        self.__obj[key] = value
        self.__keys.add(key)

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
