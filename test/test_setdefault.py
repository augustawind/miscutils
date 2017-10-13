from utils.setdefault import setdefault


class TestSetDefaultBasics:

    def test_value_none(self):
        assert setdefault(None, 5) == 5

    def test_default_none(self):
        assert setdefault(5, None) == 5

    def test_cls_param(self):
        assert setdefault(None, 5, cls=str) == '5'
        assert setdefault(5, None, cls=str) == '5'

    def test_cls_param_none(self):
        from collections import OrderedDict
        value = OrderedDict((('a', 1), ('b', 2)))
        assert type(setdefault(value, None)) == OrderedDict
        assert type(setdefault(None, value)) == OrderedDict
