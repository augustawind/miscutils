from collections import Counter, OrderedDict, defaultdict, deque
from functools import partial

import pytest

from miscutils.merge import merge
from miscutils.setdefault import setdefault


class SetDefaultTestBase:
    value = NotImplemented
    default = NotImplemented
    cls_builtin = NotImplemented
    cls_other = NotImplemented

    func = NotImplemented
    setdefault_kwargs = NotImplemented
    calculated_value = NotImplemented

    def test_both_values(self):
        assert self.func(self.value, self.default) == self.calculated_value

    def test_none_value(self):
        assert self.func(None, self.default) == self.default

    def test_none_default(self):
        assert self.func(self.value, None) == self.value

    def test_both_values_with_cls(self):
        assert self.func(self.value, self.default, cls=self.cls_builtin) == \
            self.cls_builtin(self.calculated_value)

    def test_one_value_with_cls(self):
        assert self.func(None, self.value, cls=self.cls_builtin) == \
            self.cls_builtin(self.value)
        assert self.func(self.value, None, cls=self.cls_builtin) == \
            self.cls_builtin(self.value)

    def test_one_value_with_non_builtin_cls(self):
        value = self.cls_other()
        assert type(self.func(value, None)) == self.cls_other
        assert type(self.func(None, value)) == self.cls_other

    def test_shorthand_function_vs_kwarg(self):
        assert self.func(self.value, self.default) == \
            setdefault(self.value, self.default, **self.setdefault_kwargs)


class TestSetDefaultSimple(SetDefaultTestBase):

    @pytest.fixture(autouse=True)
    def setup(self):
        self.value = 5
        self.default = 11
        self.cls_builtin = str
        self.cls_other = OrderedDict

        self.func = setdefault
        self.setdefault_kwargs = {}
        self.calculated_value = self.value

        yield


class TestSetDefaultMergeDicts(SetDefaultTestBase):

    @pytest.fixture(autouse=True)
    def setup(self):
        self.value = {'a': 1, 'b': {'x': 9}}
        self.default = OrderedDict({'a': 3, 'b': {'y': 8}, 'c': 5})
        self.cls_builtin = tuple
        self.cls_other = defaultdict

        self.func = partial(setdefault.merge_dicts, depth=-1)
        self.setdefault_kwargs = {'merge_dicts': True}
        self.calculated_value = merge(self.default, self.value, _depth=-1)

        yield


class TestSetDefaultMergeSets(SetDefaultTestBase):

    @pytest.fixture(autouse=True)
    def setup(self):
        self.value = frozenset(('a', 'b', 'c'))
        self.default = {'c', 'd'}
        self.cls_builtin = sorted
        self.cls_other = deque

        self.func = setdefault.merge_sets
        self.setdefault_kwargs = {'merge_sets': True}
        self.calculated_value = frozenset(('a', 'b', 'c', 'd'))

        yield


class TestSetDefaultMergeLists(SetDefaultTestBase):

    @pytest.fixture(autouse=True)
    def setup(self):
        self.value = [1, 2, 3]
        self.default = [-1, 0]
        #self.value = [('a', 0) ('b', 1) ('c', 2)]
        #self.default = [(-1, 'Y'), (0, 'Z')]
        self.cls_builtin = dict.fromkeys
        self.cls_other = bytearray

        self.func = setdefault.merge_lists
        self.setdefault_kwargs = {'merge_lists': True}
        self.calculated_value = [-1, 0, 1, 2, 3]
