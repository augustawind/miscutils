from utils.setdefault import setdefault


class TestSetDefaultBasics:

    def test_both_values(self):
        assert setdefault(5, 11) == 5
        assert setdefault(11, 5) == 11

    def test_one_value(self):
        assert setdefault(None, 5) == 5
        assert setdefault(5, None) == 5

    def test_one_value_with_cls(self):
        assert setdefault(None, 5, cls=str) == '5'
        assert setdefault(5, None, cls=str) == '5'

    def test_both_values_with_cls(self):
        assert setdefault(5, 11, cls=str) == '5'
        assert setdefault(11, 5, cls=str) == '11'

    def test_cls_param_none(self):
        from collections import OrderedDict
        value = OrderedDict((('a', 1), ('b', 2)))
        assert type(setdefault(value, None)) == OrderedDict
        assert type(setdefault(None, value)) == OrderedDict


