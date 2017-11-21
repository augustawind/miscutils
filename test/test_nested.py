import pytest

from utils import nested


class TestNestedGet:

    def test_01_dict(self):
        value = {'foo': 5}
        assert nested.get(value, '[foo]') == 5
        value = {'foo': {'bar': 6}}
        assert nested.get(value, '[foo]') == {'bar': 6}
        assert nested.get(value, '[foo][bar]') == 6

        with pytest.raises(nested.UnfinishedOperation):
            nested.get(value, '[')
        with pytest.raises(nested.UnfinishedOperation):
            nested.get(value, '[foo')
        with pytest.raises(nested.UnfinishedOperation):
            nested.get(value, '[foo][bar')
        with pytest.raises(nested.UnfinishedOperation):
            nested.get(value, '[foo[bar]')

    def test_01_list(self):
        value = [5]
        assert nested.get(value, '#0') == 5
        value = [5, 3]
        assert nested.get(value, '#0') == 5
        assert nested.get(value, '#1') == 3
        value = [5, 3, [9]]
        assert nested.get(value, '#2') == [9]
        assert nested.get(value, '#2#0') == 9
