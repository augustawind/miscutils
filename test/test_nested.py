from types import SimpleNamespace

import pytest

from utils import nested


class TestNestedGet:

    def test_01_dict(self):
        val = {'foo': 5}
        assert nested.get(val, '[foo]') == 5
        val = {'foo': {'bar': 6}}
        assert nested.get(val, '[foo]') == {'bar': 6}
        assert nested.get(val, '[foo][bar]') == 6

        val = {'foo': {'bar': 6}}
        with pytest.raises(nested.MissingValue):
            nested.get(val, '[')
        with pytest.raises(nested.MissingOpenOperator):
            nested.get(val, 'foo')
        with pytest.raises(nested.MissingOpenOperator):
            nested.get(val, '[foo]bar')
        with pytest.raises(nested.MissingCloseOperator):
            nested.get(val, '[foo')
        with pytest.raises(nested.MissingCloseOperator):
            nested.get(val, '[foo][bar')
        with pytest.raises(nested.MissingCloseOperator):
            nested.get(val, '[foo[bar]')

    def test_01_list(self):
        val = [5]
        assert nested.get(val, '#0') == 5
        val = [5, 3]
        assert nested.get(val, '#0') == 5
        assert nested.get(val, '#1') == 3
        val = [5, 3, [9]]
        assert nested.get(val, '#2') == [9]
        assert nested.get(val, '#2#0') == 9

        val = [5, 3, [9]]
        with pytest.raises(nested.MissingValue):
            nested.get(val, '#')
        with pytest.raises(nested.MissingValue):
            nested.get(val, '#2#')

    def test_01_object(self):
        val = SimpleNamespace(x=5)
        assert nested.get(val, '.x') == 5
        val = SimpleNamespace(x=5, y=3)
        assert nested.get(val, '.x') == 5
        assert nested.get(val, '.y') == 3
        val = SimpleNamespace(x=5, y=3, z=SimpleNamespace(a=9))
        assert nested.get(val, '.z') == SimpleNamespace(a=9)
        assert nested.get(val, '.z.a') == 9
