from collections import OrderedDict, defaultdict
from functools import partial

import pytest

from utils.merge import merge
from utils.setdefault import setdefault


class SetDefaultTestBase:

    func = setdefault

    value = NotImplemented
    default = NotImplemented
    cls = None
    other_cls = None

    calculated_value = NotImplemented

    def test_both_values(self):
        assert self.func(self.value, self.default) == self.calculated_value

    def test_none_value(self):
        assert self.func(None, self.default) == self.default

    def test_none_default(self):
        assert self.func(self.value, None) == self.value

    def test_both_values_with_cls(self):
        assert self.func(self.value, self.default, cls=self.cls) == \
            self.cls(self.calculated_value)

    def test_one_value_with_cls(self):
        assert self.func(None, self.value, cls=self.cls) == \
            self.cls(self.value)
        assert self.func(self.value, None, cls=self.cls) == \
            self.cls(self.value)

    def test_one_value_with_non_builtin_cls(self):
        value = self.other_cls()
        assert type(self.func(value, None)) == self.other_cls
        assert type(self.func(None, value)) == self.other_cls


class TestSetDefaultSimple(SetDefaultTestBase):

    @pytest.fixture(autouse=True)
    def setup(self):
        self.func = setdefault

        self.value = 5
        self.default = 11
        self.cls = str
        self.other_cls = OrderedDict

        self.calculated_value = self.value


class TestSetDefaultMergeDicts:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.func = partial(setdefault.merge_dicts, depth=-1)

        self.value = {'a': 1, 'b': {'x': 9}}
        self.default = {'a': 3, 'b': {'y': 8}, 'c': 5}
        self.cls = tuple
        self.other_cls = OrderedDict

        self.calculated_value = merge(self.default, self.value)
