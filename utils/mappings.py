from collections.abc import Mapping


class Namespace(dict):
    """A dict that supports dot-access on its items."""

    def __getstate__(self):
        return self.copy()

    def __setstate__(self, state):
        self.update(state)

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
