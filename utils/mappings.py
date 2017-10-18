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

