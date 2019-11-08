from functools import update_wrapper

__all__ = ["classproperty"]


class classproperty:
    """Turn a classmethod into a read-only property descriptor."""

    def __init__(self, method=None):
        self.fget = method
        update_wrapper(self, method)

    def __get__(self, instance, cls=None):
        return self.fget(cls)

    def getter(self, method):
        self.fget = method
        return self
