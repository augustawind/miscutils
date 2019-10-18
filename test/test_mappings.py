import copy

import pytest

from utils import mappings as maps


class MappingTest:

    @pytest.fixture
    def items1(self):
        return (('a', 0), ('b', 1), ('c', 2))

    @pytest.fixture
    def items2(self):
        return (('z', 9), ('y', 8), ('x', 7))


class TestDictSet(MappingTest):

    def test_dict_basics(self, items1):
        d = maps.DictSet(items1)
        assert len(d) == len(items1)
        for k, v in items1:
            assert d[k] == v
            d[k] += 1
            del d[k]
        assert len(d) == 0

    def test_set_ops(self):
        dx = maps.DictSet((('a', 0), ('b', 1), ('c', 2)))

        # disjoint
        assert dx.isdisjoint({'x', 'y', 'z'})
        assert dx.isdisjoint(maps.DictSet(x=0, y=1, z=2))
        assert not dx.isdisjoint(maps.DictSet(a=5))

        # subset/superset
        dxx = maps.DictSet(dx)
        assert dx <= dxx
        assert dx >= dxx
        assert not dx < dxx
        assert not dx > dxx

        # proper subset/superset
        dxx['d'] = 3
        assert dx < dxx
        assert dxx > dx

        # union
        dy = maps.DictSet(c=3, d=4)
        assert dx | dy == maps.DictSet(a=0, b=1, c=3, d=4)
        assert dy | dx == maps.DictSet(a=0, b=1, c=2, d=4)

        # intersection
        assert dx & dy == maps.DictSet(c=2)
        assert dy & dx == maps.DictSet(c=3)

        # difference
        assert dx - dy == maps.DictSet(a=0, b=1)
        assert dy - dx == maps.DictSet(d=4)

        # symmetric difference
        assert dx ^ dy == maps.DictSet(a=0, b=1, d=4)
        assert dy ^ dx == maps.DictSet(a=0, b=1, d=4)

    def test_copy(self):
        ns = maps.DictSet((('a', 0), ('b', maps.DictSet(x=9)), ('c', 5)))
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