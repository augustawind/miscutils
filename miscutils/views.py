"""views - mutable slices of compound data types"""
from collections.abc import Iterable, Mapping, MutableMapping, MutableSet


class SetView(MutableSet):
    """A slice of a set that allows mutable access to a subset of its items."""

    def __init__(self, obj: MutableSet, values: Iterable):
        self.__obj = obj
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
        try:
            self.remove(value)
        except KeyError:
            pass

    def remove(self, value):
        self.__values.remove(value)
        self.__obj.discard(value)

    def clear(self):
        self.__obj -= self.__values
        self.__values.clear()

    def pop(self):
        item = self.__values.pop()
        self.__obj.discard(item)
        return item

    def __ior__(self, other):
        self.__values |= other
        return self

    def __iand__(self, other):
        self.__values &= other
        return self

    def __ixor__(self, other):
        self.__values ^= other
        return self

    def __isub__(self, other):
        self.__values -= other
        return self


class DictView(MutableMapping):
    """A slice of a dict that allows mutable access to a subset of its keys."""

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
