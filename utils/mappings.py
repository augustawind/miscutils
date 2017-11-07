from collections.abc import Mapping


def subset(m0, m1):
    return {k: v for k, v in m0.items() if k in m1}


class Namespace(dict):
    """A dict that supports dot-access on its items."""

    def __getattr__(self, attr):
        return self.__getitem__(attr)

    def __setattr__(self, key, value):
        return self.__setitem__(key, value)


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


class MultiDict(dict):

    def __init__(self, *args, **kwargs):
        items = dict(*args, **kwargs).items()
        super().__init__((k, val) for key, val in items for k in key)
