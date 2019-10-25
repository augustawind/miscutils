"""functional - functional programming in Python"""
from typing import Any, Callable, Generic, Tuple, TypeVar, Union

from .merge import merge


class F:
    """Function wrapper that adds functional programming features."""

    def __init__(self, f: callable):
        self.f = f


R = TypeVar('R')


class Curried(Generic[R]):
    def __init__(self, f: Callable[..., R], *args: Any, **kwargs: Any):
        self._f = f
        self._nargs = f.__code__.co_argcount - len(f.__defaults__ or ())
        self._args = ()
        self._kwargs = {}

        self._args, self._kwargs, _ = self._apply(args, kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> Union['Curried[R]', R]:
        args, kwargs, complete = self._apply(args, kwargs)

        if complete:
            return self._f(*args, **kwargs)

        return Curried(self._f, *args, **kwargs)

    def _apply(self, args: tuple, kwargs: dict) -> Tuple[tuple, dict, bool]:
        args = self._args + args
        kwargs = merge({}, self._kwargs, kwargs, _depth=0)
        complete = len(args) >= self._nargs
        return args, kwargs, complete

    def __eq__(self, other):
        return isinstance(other, Curried) and (
            self._f,
            self._nargs,
            self._args,
            self._kwargs,
        ) == (other._f, other._nargs, other._args, other._kwargs)
