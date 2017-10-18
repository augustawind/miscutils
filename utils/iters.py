from itertools import *


def cons(item, iterable):
    yield item
    yield from iterable


def rcons(item, iterable):
    yield from iterable
    yield item


def insert(i, item, iterable):
    yield from islice(iterable, i)
    yield item
    yield from islice(iterable, i, None)


def intersperse(item, iterable):
    if not hasattr(iterable, '__next__'):
        iterable = iter(iterable)
    yield next(iterable)
    for x in iterable:
        yield item
        yield x
