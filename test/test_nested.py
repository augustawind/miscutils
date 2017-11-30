from types import SimpleNamespace as Object

import pytest

from utils import nested


class TestGet:

    def test_01_mapping(self):
        val = {'x': 5}
        assert nested.get(val, '[x]') == 5
        val = {'x': 5, 'y': 3}
        assert nested.get(val, '[x]') == 5
        assert nested.get(val, '[y]') == 3
        val = {'x': {'y': 6}}
        assert nested.get(val, '[x]') == {'y': 6}
        assert nested.get(val, '[x][y]') == 6

    def test_02_mapping_validation(self):
        val = {'x': {'y': 6}}
        with pytest.raises(nested.MissingValueChar):
            nested.get(val, '[')
        with pytest.raises(nested.MissingLHSOperator):
            nested.get(val, 'x')
        with pytest.raises(nested.MissingLHSOperator):
            nested.get(val, '[x]y')
        with pytest.raises(nested.MissingRHSOperator):
            nested.get(val, '[x')
        with pytest.raises(nested.MissingRHSOperator):
            nested.get(val, '[x][y')
        with pytest.raises(nested.MissingRHSOperator):
            nested.get(val, '[x[y]')
        with pytest.raises(KeyError):
            nested.get(val, '[x][z]')

    def test_01_sequence(self):
        val = [5]
        assert nested.get(val, '#0') == 5
        val = [5, 3]
        assert nested.get(val, '#0') == 5
        assert nested.get(val, '#1') == 3
        val = [5, 3, [9]]
        assert nested.get(val, '#2') == [9]
        assert nested.get(val, '#2#0') == 9

    def test_02_sequence_validation(self):
        val = [5, 3, [9]]
        with pytest.raises(nested.MissingValueChar):
            nested.get(val, '#')
        with pytest.raises(nested.MissingValueChar):
            nested.get(val, '#2#')
        with pytest.raises(IndexError):
            nested.get(val, '#2#1')

    def test_01_object(self):
        val = Object(x=5)
        assert nested.get(val, '.x') == 5
        val = Object(x=5, y=3)
        assert nested.get(val, '.x') == 5
        assert nested.get(val, '.y') == 3
        val = Object(x=5, y=3, z=Object(a=9))
        assert nested.get(val, '.z') == Object(a=9)
        assert nested.get(val, '.z.a') == 9

    def test_02_object_validation(self):
        val = Object(x=5, y=3, z=Object(a=9))
        with pytest.raises(nested.MissingValueChar):
            nested.get(val, '.')
        with pytest.raises(nested.MissingValueChar):
            nested.get(val, '.z.')
        with pytest.raises(AttributeError):
            nested.get(val, '.z.b')

    @staticmethod
    def _make_mixed_mapping():
        return {'x':
                [5,
                 [Object(
                     y={
                         'z':9})]]}

    def test_03_mapping_mixed(self):
        val = self._make_mixed_mapping()
        assert nested.get(val, '[x]#0') == 5
        assert nested.get(val, '[x]#1#0.y') == {'z': 9}
        assert nested.get(val, '[x]#1#0.y[z]') == 9

    def test_04_mapping_mixed_validation(self):
        val = self._make_mixed_mapping()
        with pytest.raises(nested.MissingValueChar):
            nested.get(val, '[x]#')
        with pytest.raises(nested.MissingValueChar):
            nested.get(val, '[x]#1#0.')
        with pytest.raises(nested.MissingValueChar):
            nested.get(val, '[x]#1#0.y[')
        with pytest.raises(nested.MissingLHSOperator):
            nested.get(val, '[x]1')
        with pytest.raises(nested.MissingRHSOperator):
            nested.get(val, '[x]#1#0.y[z')
        with pytest.raises(nested.UnexpectedRHSOperator):
            nested.get(val, '[x]#1#0.yz]')

    @staticmethod
    def _make_mixed_sequence():
        return [True,
                {'x':
                 {'y':
                  Object(
                      z=[9])}}]

    def test_03_sequence_mixed(self):
        val = self._make_mixed_sequence()
        assert nested.get(val, '#0') == True
        assert nested.get(val, '#1[x][y]') == Object(z=[9])
        assert nested.get(val, '#1[x][y].z#0') == 9

    def test_04_sequence_mixed_validation(self):
        val = self._make_mixed_sequence()
        with pytest.raises(nested.MissingValueChar):
            nested.get(val, '#1[')
        with pytest.raises(nested.MissingValueChar):
            nested.get(val, '#1[x][y].')
        with pytest.raises(IndexError):
            nested.get(val, '#2')

    @staticmethod
    def _make_mixed_object():
        return Object(x=
                      Object(y={
                          'z': 5, 'a': [
                              -2,
                              {'b': 9}]}))

    def test_03_object_mixed(self):
        val = self._make_mixed_object()
        assert nested.get(val, '.x.y[z]') == 5
        assert nested.get(val, '.x.y[a]#0') == -2
        assert nested.get(val, '.x.y[a]#1') == {'b': 9}
        assert nested.get(val, '.x.y[a]#1[b]') == 9

    def test_04_object_mixed_validation(self):
        val = self._make_mixed_object()
        with pytest.raises(nested.MissingValueChar):
            nested.get(val, '.x.')
        with pytest.raises(nested.MissingValueChar):
            nested.get(val, '.x.y[a]#')
        with pytest.raises(AttributeError):
            nested.get(val, '.x.z')
