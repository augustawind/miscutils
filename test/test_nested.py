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
        data = {'x': 5}
        assert nested.get(data, '[x]') == 5
        data = {'x': 5, 'y': 3}
        assert nested.get(data, '[x]') == 5
        assert nested.get(data, '[y]') == 3
        data = {'x': {'y': 6}}
        assert nested.get(data, '[x]') == {'y': 6}
        assert nested.get(data, '[x][y]') == 6

    def test_01_sequence(self):
        data = [5]
        assert nested.get(data, '#0') == 5
        data = [5, 3]
        assert nested.get(data, '#0') == 5
        assert nested.get(data, '#1') == 3
        data = [5, 3, [9]]
        assert nested.get(data, '#2') == [9]
        assert nested.get(data, '#2#0') == 9

    def test_01_object(self):
        data = Object(x=5)
        assert nested.get(data, '.x') == 5
        data = Object(x=5, y=3)
        assert nested.get(data, '.x') == 5
        assert nested.get(data, '.y') == 3
        data = Object(x=5, y=3, z=Object(a=9))
        assert nested.get(data, '.z') == Object(a=9)
        assert nested.get(data, '.z.a') == 9

    def test_02_mapping_validation(self):
        data = {'x': {'y': 6}}
        self.check_mapping_validation(data, nested.get)

    def test_02_sequence_validation(self):
        data = [5, 3, [9]]
        self.check_sequence_validation(data, nested.get)

    def test_02_object_validation(self):
        data = Object(x=5, y=3, z=Object(a=9))
        self.check_object_validation(data, nested.get)

    def test_03_mapping_mixed(self):
        data = self._make_mixed_mapping()
        assert nested.get(data, '[x]#0') == 5
        assert nested.get(data, '[x]#1#0.y') == {'z': 9}
        assert nested.get(data, '[x]#1#0.y[z]') == 9

    def test_03_sequence_mixed(self):
        data = self._make_mixed_sequence()
        assert nested.get(data, '#0') == True
        assert nested.get(data, '#1[x][y]') == Object(z=[9])
        assert nested.get(data, '#1[x][y].z#0') == 9

    def test_03_object_mixed(self):
        data = self._make_mixed_object()
        assert nested.get(data, '.x.y[z]') == 5
        assert nested.get(data, '.x.y[a]#0') == -2
        assert nested.get(data, '.x.y[a]#1') == {'b': 9}
        assert nested.get(data, '.x.y[a]#1[b]') == 9

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
        nested.set(data, '.x', value=8)
        assert data.x == 8

        data = Object(x=5, y=3)
        nested.set(data, '.x', value=8)
        assert data.x == 8
        nested.set(data, '.y', value=-2)
        assert data.x == 8
        assert data.y == -2

        data = Object(x=5, y=3, z=Object(a=9))
        nested.set(data, '.z', value=Object(a=12))
        assert data.z == Object(a=12)
        nested.set(data, '.z.a', value=7)
        assert data.z.a == 7

    def test_02_mapping_validation(self):
        data = {'x': {'y': 6}}
        self.check_mapping_validation(data, nested.set, value=9)

    def test_02_sequence_validation(self):
        data = [5, 3, [9]]
        self.check_sequence_validation(data, nested.set, value=12)

    def test_02_object_validation(self):
        data = Object(x=5, y=3, z=Object(a=9))
        self.check_object_validation(data, nested.set, value=12)

    def test_03_mapping_mixed(self):
        data = self._make_mixed_mapping()
        nested.set(data, '[x]#0', value=8)
        assert data['x'][0] == 8

        nested.set(data, '[x]#1#0.y', value={'z': 12})
        assert data['x'][0] == 8
        assert data['x'][1][0].y == {'z': 12}

        nested.set(data, '[x]#1#0.y[z]', value=-3)
        assert data['x'][0] == 8
        assert data['x'][1][0].y['z'] == -3

    def test_03_sequence_mixed(self):
        data = self._make_mixed_sequence()
        nested.set(data, '#0', value=False)
        assert data[0] is False

        nested.set(data, '#1[x][y]', value=Object(z=[12]))
        assert data[0] is False
        assert data[1]['x']['y'] == Object(z=[12])

        nested.set(data, '#1[x][y].z#0', value=-3)
        assert data[0] is False
        assert data[1]['x']['y'].z[0] == -3

    def test_03_object_mixed(self):
        data = self._make_mixed_object()
        assert nested.get(data, '.x.y[z]') == 5
        assert nested.get(data, '.x.y[a]#0') == -2
        assert nested.get(data, '.x.y[a]#1') == {'b': 9}
        assert nested.get(data, '.x.y[a]#1[b]') == 9

    def test_04_mapping_mixed_validation(self):
        data = self._make_mixed_mapping()
        self.check_mapping_mixed_validation(data, nested.set, value=18)

    def test_04_sequence_mixed_validation(self):
        data = self._make_mixed_sequence()
        self.check_sequence_mixed_validation(data, nested.set, value=18)

    def test_04_object_mixed_validation(self):
        data = self._make_mixed_object()
        self.check_object_mixed_validation(data, nested.set, value=18)


class TestUpdate(Common):

    @staticmethod
    def MK_ADD(x):
        def transform(node):
            return node.value + x
        return transform

    @staticmethod
    def REPR_NODE(node):
        return '{!s}-{!s}-{!s}'.format(
            type(node.parent).__name__,
            node.action.item,
            node.value,
        )

    @staticmethod
    def CONST(value):
        def transform(_):
            return value
        return transform

    def test_01_mapping(self):
        data = {'x': 5}
        nested.update(data, '[x]', transform=self.MK_ADD(3))
        assert data['x'] == 8

        data = {'x': 5, 'y': 3}
        nested.update(data, '[x]', transform=self.MK_ADD(3))
        assert data['x'] == 8
        nested.update(data, '[y]', transform=self.REPR_NODE)
        assert data['x'] == 8
        assert data['y'] == 'dict-y-3'

        data = {'x': {'y': 6}}
        nested.update(data, '[x]', transform=self.CONST({'z': 13}))
        assert data['x'] == {'z': 13}
        nested.update(data, '[x][z]', transform=self.MK_ADD(-11))
        assert data['x']['z'] == 2

    def test_01_sequence(self):
        data = [5]
        nested.update(data, '#0', transform=self.MK_ADD(3))
        assert data[0] == 8

        data = [5, 3]
        nested.update(data, '#0', transform=self.MK_ADD(3))
        assert data[0] == 8
        nested.update(data, '#1', transform=self.REPR_NODE)
        assert data[0] == 8
        assert data[1] == 'list-1-3'

        data = [5, 3, [9]]
        nested.update(data, '#2', transform=self.CONST([12]))
        assert data[2] == [12]
        nested.update(data, '#2#0', self.REPR_NODE)
        assert data[2][0] == 'list-0-12'

    def test_01_object(self):
        data = Object(x=5)
        nested.update(data, '.x', transform=self.MK_ADD(3))
        assert data.x == 8

        data = Object(x=5, y=3)
        nested.update(data, '.x', transform=self.MK_ADD(3))
        assert data.x == 8
        nested.update(data, '.y', transform=self.REPR_NODE)
        assert data.x == 8
        assert data.y == 'SimpleNamespace-y-3'

        data = Object(x=5, y=3, z=Object(a=9))
        nested.update(data, '.z', transform=self.CONST(Object(a=12)))
        assert data.z == Object(a=12)
        nested.update(data, '.z.a', transform=self.REPR_NODE)
        assert data.z.a == 'SimpleNamespace-a-12'

#    def test_02_mapping_validation(self):
#        data = {'x': {'y': 6}}
#        self.check_mapping_validation(data, nested.set, value=9)
#
#    def test_02_sequence_validation(self):
#        data = [5, 3, [9]]
#        self.check_sequence_validation(data, nested.set, value=12)
#
#    def test_02_object_validation(self):
#        data = Object(x=5, y=3, z=Object(a=9))
#        self.check_object_validation(data, nested.set, value=12)
#
#    def test_03_mapping_mixed(self):
#        data = self._make_mixed_mapping()
#        nested.set(data, '[x]#0', value=8)
#        assert data['x'][0] == 8
#
#        nested.set(data, '[x]#1#0.y', value={'z': 12})
#        assert data['x'][0] == 8
#        assert data['x'][1][0].y == {'z': 12}
#
#        nested.set(data, '[x]#1#0.y[z]', value=-3)
#        assert data['x'][0] == 8
#        assert data['x'][1][0].y['z'] == -3
#
#    def test_03_sequence_mixed(self):
#        data = self._make_mixed_sequence()
#        nested.set(data, '#0', value=False)
#        assert data[0] is False
#
#        nested.set(data, '#1[x][y]', value=Object(z=[12]))
#        assert data[0] is False
#        assert data[1]['x']['y'] == Object(z=[12])
#
#        nested.set(data, '#1[x][y].z#0', value=-3)
#        assert data[0] is False
#        assert data[1]['x']['y'].z[0] == -3
#
#    def test_03_object_mixed(self):
#        data = self._make_mixed_object()
#        assert nested.get(data, '.x.y[z]') == 5
#        assert nested.get(data, '.x.y[a]#0') == -2
#        assert nested.get(data, '.x.y[a]#1') == {'b': 9}
#        assert nested.get(data, '.x.y[a]#1[b]') == 9
#
#    def test_04_mapping_mixed_validation(self):
#        data = self._make_mixed_mapping()
#        self.check_mapping_mixed_validation(data, nested.set, value=18)
#
#    def test_04_sequence_mixed_validation(self):
#        data = self._make_mixed_sequence()
#        self.check_sequence_mixed_validation(data, nested.set, value=18)
#
#    def test_04_object_mixed_validation(self):
#        data = self._make_mixed_object()
#        self.check_object_mixed_validation(data, nested.set, value=18)
