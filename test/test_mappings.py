import pytest

from utils import mappings as maps


def test_namespace():
    ns = maps.Namespace((('a', 0), ('b', 1)), c=2)
    assert ns.a == ns['a'] == 0
    assert ns.b == ns['b'] == 1
    assert ns.c == ns['c'] == 2
    assert set(ns.items()) == set((('a', 0), ('b', 1), ('c', 2)))
    ns.d = 3
    ns.e = 4
    assert ns.d == ns['d'] == 3
    assert ns.e == ns['e'] == 4
    with pytest.raises(KeyError):
        ns.x
    with pytest.raises(KeyError):
        ns['x']


def test_frozendict():
    items = (('a', 0), ('b', 1), ('c', 2))
    non_items = (('z', 9), ('y', 8), ('x', 7))
    dicts = (
        maps.FrozenDict(items),
        maps.FrozenDict(items[:1], **dict(items[1:])),
        maps.FrozenDict(**dict(items)),
    )
    for d in dicts:
        for k, v in items:
            assert d[k] == v
        for k, v in non_items:
            with pytest.raises(TypeError):
                d[k] = v
            with pytest.raises(KeyError):
                d[k]
