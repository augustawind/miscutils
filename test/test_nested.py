from types import SimpleNamespace as Object

import pytest

from utils import nested


class Common:

    def check_mapping_validation(self, data, func, *args, **kwargs):
        with pytest.raises(nested.MissingValueChar):
            func(data, '[', *args, **kwargs)
        with pytest.raises(nested.MissingLHSOperator):
            func(data, 'x', *args, **kwargs)
        with pytest.raises(nested.MissingLHSOperator):
            func(data, '[x]y', *args, **kwargs)
        with pytest.raises(nested.MissingRHSOperator):
            func(data, '[x', *args, **kwargs)
        with pytest.raises(nested.MissingRHSOperator):
            func(data, '[x][y', *args, **kwargs)
        with pytest.raises(nested.MissingRHSOperator):
            func(data, '[x[y]', *args, **kwargs)
        with pytest.raises(KeyError):
            func(data, '[x][z]', *args, **kwargs)

    def check_sequence_validation(self, data, func, *args, **kwargs):
        with pytest.raises(nested.MissingValueChar):
            func(data, '#', *args, **kwargs)
        with pytest.raises(nested.MissingValueChar):
            func(data, '#2#', *args, **kwargs)
        with pytest.raises(IndexError):
            func(data, '#2#1', *args, **kwargs)

    def check_object_validation(self, data, func, *args, **kwargs):
        with pytest.raises(nested.MissingValueChar):
            func(data, '.', *args, **kwargs)
        with pytest.raises(nested.MissingValueChar):
            func(data, '.z.', *args, **kwargs)
        with pytest.raises(AttributeError):
            func(data, '.z.b', *args, **kwargs)

    def check_mapping_mixed_validation(self, data, func, *args, **kwargs):
        with pytest.raises(nested.MissingValueChar):
            func(data, '[x]#', *args, **kwargs)
        with pytest.raises(nested.MissingValueChar):
            func(data, '[x]#1#0.', *args, **kwargs)
        with pytest.raises(nested.MissingValueChar):
            func(data, '[x]#1#0.y[', *args, **kwargs)
        with pytest.raises(nested.MissingLHSOperator):
            func(data, '[x]1', *args, **kwargs)
        with pytest.raises(nested.MissingRHSOperator):
            func(data, '[x]#1#0.y[z', *args, **kwargs)
        with pytest.raises(nested.UnexpectedRHSOperator):
            func(data, '[x]#1#0.yz]', *args, **kwargs)

    def check_sequence_mixed_validation(self, data, func, *args, **kwargs):
        with pytest.raises(nested.MissingValueChar):
            func(data, '#1[', *args, **kwargs)
        with pytest.raises(nested.MissingValueChar):
            func(data, '#1[x][y].', *args, **kwargs)
        with pytest.raises(IndexError):
            func(data, '#2', *args, **kwargs)

    def check_object_mixed_validation(self, data, func, *args, **kwargs):
        with pytest.raises(nested.MissingValueChar):
            func(data, '.x.', *args, **kwargs)
        with pytest.raises(nested.MissingValueChar):
            func(data, '.x.y[a]#', *args, **kwargs)
        with pytest.raises(AttributeError):
            func(data, '.x.z', *args, **kwargs)

    @staticmethod
    def _make_mixed_mapping():
        return {'x':
                [5,
                 [Object(
                     y={
                         'z':9})]]}

    @staticmethod
    def _make_mixed_sequence():
        return [True,
                {'x':
                 {'y':
                  Object(
                      z=[9])}}]

    @staticmethod
    def _make_mixed_object():
        return Object(x=
                      Object(y={
                          'z': 5, 'a': [
                              -2,
                              {'b': 9}]}))


class TestGet(Common):

    def test_01_mapping(self):
        val = {'x': 5}
        assert nested.get(val, '[x]') == 5
        val = {'x': 5, 'y': 3}
        assert nested.get(val, '[x]') == 5
        assert nested.get(val, '[y]') == 3
        val = {'x': {'y': 6}}
        assert nested.get(val, '[x]') == {'y': 6}
        assert nested.get(val, '[x][y]') == 6

    def test_01_sequence(self):
        val = [5]
        assert nested.get(val, '#0') == 5
        val = [5, 3]
        assert nested.get(val, '#0') == 5
        assert nested.get(val, '#1') == 3
        val = [5, 3, [9]]
        assert nested.get(val, '#2') == [9]
        assert nested.get(val, '#2#0') == 9

    def test_01_object(self):
        val = Object(x=5)
        assert nested.get(val, '.x') == 5
        val = Object(x=5, y=3)
        assert nested.get(val, '.x') == 5
        assert nested.get(val, '.y') == 3
        val = Object(x=5, y=3, z=Object(a=9))
        assert nested.get(val, '.z') == Object(a=9)
        assert nested.get(val, '.z.a') == 9

    def test_02_mapping_validation(self):
        val = {'x': {'y': 6}}
        self.check_mapping_validation(val, nested.get)

    def test_02_sequence_validation(self):
        data = [5, 3, [9]]
        self.check_sequence_validation(data, nested.get)

    def test_02_object_validation(self):
        data = Object(x=5, y=3, z=Object(a=9))
        self.check_object_validation(data, nested.get)

    def test_03_mapping_mixed(self):
        val = self._make_mixed_mapping()
        assert nested.get(val, '[x]#0') == 5
        assert nested.get(val, '[x]#1#0.y') == {'z': 9}
        assert nested.get(val, '[x]#1#0.y[z]') == 9

    def test_03_sequence_mixed(self):
        val = self._make_mixed_sequence()
        assert nested.get(val, '#0') == True
        assert nested.get(val, '#1[x][y]') == Object(z=[9])
        assert nested.get(val, '#1[x][y].z#0') == 9

    def test_03_object_mixed(self):
        val = self._make_mixed_object()
        assert nested.get(val, '.x.y[z]') == 5
        assert nested.get(val, '.x.y[a]#0') == -2
        assert nested.get(val, '.x.y[a]#1') == {'b': 9}
        assert nested.get(val, '.x.y[a]#1[b]') == 9

    def test_04_mapping_mixed_validation(self):
        data = self._make_mixed_mapping()
        self.check_mapping_mixed_validation(data, nested.get)

    def test_04_sequence_mixed_validation(self):
        data = self._make_mixed_sequence()
        self.check_sequence_mixed_validation(data, nested.get)

    def test_04_object_mixed_validation(self):
        data = self._make_mixed_object()
        self.check_object_mixed_validation(data, nested.get)


class TestSet(Common):

    def test_01_mapping(self):
        data = {'x': 5}
        nested.set(data, '[x]', value=8)
        assert data['x'] == 8

        data = {'x': 5, 'y': 3}
        nested.set(data, '[x]', value=8)
        assert data['x'] == 8
        nested.set(data, '[y]', value=-2)
        assert data['x'] == 8
        assert data['y'] == -2

        data = {'x': {'y': 6}}
        nested.set(data, '[x]', value={'z': 13})
        assert data['x'] == {'z': 13}
        nested.set(data, '[x][z]', value=2)
        assert data['x']['z'] == 2

    def test_01_sequence(self):
        data = [5]
        nested.set(data, '#0', value=8)
        assert data[0] == 8

        data = [5, 3]
        nested.set(data, '#0', value=8)
        assert data[0] == 8
        nested.set(data, '#1', value=-2)
        assert data[0] == 8
        assert data[1] == -2

        data = [5, 3, [9]]
        nested.set(data, '#2', value=[12])
        assert data[2] == [12]
        nested.set(data, '#2#0', value=7)
        assert data[2][0] == 7

    def test_01_object(self):
        data = Object(x=5)
        nested.set(data, '.x', 8)
        assert data.x == 8

        data = Object(x=5, y=3)
        nested.set(data, '.x', 8)
        assert data.x == 8
        nested.set(data, '.y', -2)
        assert data.x == 8
        assert data.y == -2

        data = Object(x=5, y=3, z=Object(a=9))
        nested.set(data, '.z', Object(a=12))
        assert data.z == Object(a=12)
        nested.set(data, '.z.a', 7)
        assert data.z.a == 7

    def test_02_mapping_validation(self):
        data = {'x': {'y': 6}}
        self.check_mapping_validation(data, nested.set, value=9)

    def test_02_sequence_validation(self):
        data = [5, 3, [9]]
        self.check_sequence_validation(data, nested.set, value=12)

    def test_02_object_validation(self):
        data = Object(x=5, y=3, z=Object(a=9))
        self.check_object_validation(data, nested.set, 12)

#    @staticmethod
#    def _make_mixed_mapping():
#        return {'x':
#                [5,
#                 [Object(
#                     y={
#                         'z':9})]]}
#
#    def test_03_mapping_mixed(self):
#        val = self._make_mixed_mapping()
#        assert nested.get(val, '[x]#0') == 5
#        assert nested.get(val, '[x]#1#0.y') == {'z': 9}
#        assert nested.get(val, '[x]#1#0.y[z]') == 9
#
#    def test_04_mapping_mixed_validation(self):
#        val = self._make_mixed_mapping()
#        with pytest.raises(nested.MissingValueChar):
#            nested.get(val, '[x]#')
#        with pytest.raises(nested.MissingValueChar):
#            nested.get(val, '[x]#1#0.')
#        with pytest.raises(nested.MissingValueChar):
#            nested.get(val, '[x]#1#0.y[')
#        with pytest.raises(nested.MissingLHSOperator):
#            nested.get(val, '[x]1')
#        with pytest.raises(nested.MissingRHSOperator):
#            nested.get(val, '[x]#1#0.y[z')
#        with pytest.raises(nested.UnexpectedRHSOperator):
#            nested.get(val, '[x]#1#0.yz]')
#
#    @staticmethod
#    def _make_mixed_sequence():
#        return [True,
#                {'x':
#                 {'y':
#                  Object(
#                      z=[9])}}]
#
#    def test_03_sequence_mixed(self):
#        val = self._make_mixed_sequence()
#        assert nested.get(val, '#0') == True
#        assert nested.get(val, '#1[x][y]') == Object(z=[9])
#        assert nested.get(val, '#1[x][y].z#0') == 9
#
#    def test_04_sequence_mixed_validation(self):
#        val = self._make_mixed_sequence()
#        with pytest.raises(nested.MissingValueChar):
#            nested.get(val, '#1[')
#        with pytest.raises(nested.MissingValueChar):
#            nested.get(val, '#1[x][y].')
#        with pytest.raises(IndexError):
#            nested.get(val, '#2')
#
#    @staticmethod
#    def _make_mixed_object():
#        return Object(x=
#                      Object(y={
#                          'z': 5, 'a': [
#                              -2,
#                              {'b': 9}]}))
#
#    def test_03_object_mixed(self):
#        val = self._make_mixed_object()
#        assert nested.get(val, '.x.y[z]') == 5
#        assert nested.get(val, '.x.y[a]#0') == -2
#        assert nested.get(val, '.x.y[a]#1') == {'b': 9}
#        assert nested.get(val, '.x.y[a]#1[b]') == 9
#
#    def test_04_object_mixed_validation(self):
#        val = self._make_mixed_object()
#        with pytest.raises(nested.MissingValueChar):
#            nested.get(val, '.x.')
#        with pytest.raises(nested.MissingValueChar):
#            nested.get(val, '.x.y[a]#')
#        with pytest.raises(AttributeError):
#            nested.get(val, '.x.z')
