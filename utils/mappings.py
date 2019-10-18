from collections.abc import Mapping, Set
class DictSet(dict, Set):
    """A dict that also functions as a set over its keys."""

    # def __init__(self, iterable=(), **kwargs):
    #     self.__dict = dict(iterable, **kwargs)

    # def __contains__(self, item):
    #     return item in self.__dict

    # def __iter__(self):
    #     return iter(self.__dict)

    # def __len__(self):
    #     return len(self.__dict)

    # def __getitem__(self, key):
    #     return self.__dict[key]

    # def __setitem__(self, key, value):
    #     self.__dict[key] = value

    # def __delitem__(self, key):
    #     del self.__dict[key]


class FrozenDict(Mapping):
    """A dict whose items cannot be modified."""

    def __init__(self, iterable=(), **kwargs):
        self.__dict = dict(iterable, **kwargs)

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
        self = state

    __deepcopy__ = None


class FrozenNamespace(FrozenDict):
    """A ``FrozenDict`` that supports dot-access of its keys."""

    def __getattr__(self, attr):
        return self.__dict[attr]
