"""functional - functional programming in Python"""
from copy import copy
from typing import Any, Callable, Generic, Tuple, TypeVar, Union

from .merge import merge

__all__ = ["curried", "CurriedFunc"]


class F:
    """Function wrapper that adds functional programming features."""

    def __init__(self, f: callable):
        self.f = f


class DEFAULT:
    """Non-None default value."""


R = TypeVar("R")


class CurriedFunc(Generic[R]):
    def __init__(self, f: Callable[..., R], *args: Any, **kwargs: Any):
        self._f = f
        argnames = f.__code__.co_varnames
        nkwargs = (len(f.__defaults__ or ())) + f.__code__.co_kwonlyargcount
        self._argnames = argnames[: len(argnames) - nkwargs]
        self._args_map = dict.fromkeys(self._argnames, DEFAULT)
        self._kwargs = {}

        self._args_map, self._kwargs, _ = self._apply(
            self._args_map, args, kwargs
        )

    def __call__(
        self, *args: Any, **kwargs: Any
    ) -> Union["CurriedFunc[R]", R]:
        args_map, kwargs, complete = self._apply(
            self._args_map.copy(), args, kwargs
        )

        if complete:
            return self._f(*(args_map[k] for k in self._argnames), **kwargs)

        next_f = copy(self)
        next_f._args_map = args_map
        next_f._kwargs = kwargs
        return next_f

    def _apply(
        self, args_map: dict, args: tuple, kwargs: dict
    ) -> Tuple[dict, dict, bool]:
        # Populate positional args from `kwargs`, if any
        del_keys = []
        for key, val in kwargs.items():
            if key in args_map:
                args_map[key] = val
                del_keys.append(key)
        for key in del_keys:
            del kwargs[key]

        # Populate positional args from `args`
        for arg in args:
            for key in self._argnames:
                if args_map[key] is DEFAULT:
                    args_map[key] = arg
                    break

        # Populate keyword args from remaining `kwargs`
        kwargs = merge({}, self._kwargs, kwargs, _depth=0)

        complete = all(arg is not DEFAULT for arg in args_map.values())
        return args_map, kwargs, complete

    def __eq__(self, other):
        return isinstance(other, CurriedFunc) and (
            self._f,
            self._args_map,
            self._kwargs,
        ) == (other._f, other._args_map, other._kwargs)


curried = CurriedFunc
