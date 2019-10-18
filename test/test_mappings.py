import copy

import pytest

from utils import mappings as maps


class TestNamespace:

    @pytest.fixture
    def ns(self):
        return maps.Namespace((('a', 0), ('b', 1), ('c', 2)))

    def test_create(self, ns):
        assert ns.a == ns['a'] == 0
        assert ns.b == ns['b'] == 1
        assert ns.c == ns['c'] == 2
        assert set(ns.items()) == set((('a', 0), ('b', 1), ('c', 2)))

    def test_update(self, ns):
        ns.d = 3
        ns.e = 4
        assert ns.d == ns['d'] == 3
        assert ns.e == ns['e'] == 4

    def test_bad_lookups(self, ns):
        with pytest.raises(KeyError):
            ns.x
        with pytest.raises(KeyError):
            ns['x']

    def test_copy(self):
        ns = maps.Namespace((('a', 0), ('b', maps.Namespace(x=9)), ('c', 5)))
        assert copy.copy(ns) == ns
        assert copy.deepcopy(ns) == ns


class TestFrozenDict:

    @pytest.fixture
    def items(self):
        return (('a', 0), ('b', 1), ('c', 2))

    @pytest.fixture
    def non_items(self):
        return (('z', 9), ('y', 8), ('x', 7))

    @pytest.fixture
    def dicts(self, items):
        return (
            maps.FrozenDict(items),
            maps.FrozenDict(items[:1], **dict(items[1:])),
            maps.FrozenDict(**dict(items)),
        )

    def test_existing_keys(self, dicts, items):
        for d in dicts:
            for k, v in items:
                assert d[k] == v
                with pytest.raises(TypeError):
                    d[k] = 'abc'
                with pytest.raises(TypeError):
                    del d[k]

    def test_non_existing_keys(self, dicts, non_items):
        for d in dicts:
            for k, v in non_items:
                with pytest.raises(TypeError):
                    d[k] = v
                with pytest.raises(TypeError):
                    del d[k]
                with pytest.raises(KeyError):
                    d[k]

    def test_copy(self):
        d = maps.FrozenDict(a=1, b=maps.FrozenDict(c=3))
        assert copy.copy(d) == d
        assert copy.deepcopy(d) == d
