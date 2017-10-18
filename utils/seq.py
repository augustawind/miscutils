from itertools import *


def inits(seq):
    return (seq[:i + 1] for i in range(len(seq)))


def tails(seq):
    return (seq[:i] for i in range(len(seq), 0, -1))


def cons(item, iterable):
    yield item
    yield from iterable


def rcons(item, iterable):
    yield from iterable
    yield item


def insert(i, item, iterable):
    yield from islice(iterable, i)
    yield item
    yield from iterable


def intersperse(item, iterable):
    yield next(iterable)
    for x in iterable:
        yield item
        yield x
