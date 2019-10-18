from collections.abc import Mapping, MutableMapping, Set


def subset(m0, m1):
    return {k: v for k, v in m0.items() if k in m1}


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


class _DotAccessItems:

    def __getattr__(self, attr):
        return self.__getitem__(attr)

    def __setattr__(self, key, value):
        return self.__setitem__(key, value)


class Namespace(dict, _DotAccessItems):
    """A dict that supports dot-access of its keys."""


class FrozenNamespace(FrozenDict, _DotAccessItems):
    """A ``FrozenDict`` that supports dot-access of its keys."""