import pytest

from utils.envparse import EnvSettings, Param, InvalidParam


class TestParam:

    def test_validation(self):
        with pytest.raises(
            InvalidParam,
            match='foo',
            message='should not permit required=False without a default',
        ):
            Param(3, required=False).register('foo', None, [])
        with pytest.raises(
            InvalidParam,
            message='should not permit required=True with a default',
        ):
            Param(3, default=5, required=True).register('foo', None, [])

        p = Param(3, default=5, required=False).register('foo', None, [])
        assert p.required is False, \
            'explicit required=False should be allowed if a default is given'
        p = Param(3, default=5).register('foo', None, [])
        assert p.required is False, \
            'required should default to False if a default is given'
        p = Param(3).register('foo', None, [])
        assert p.required is True, \
            'required should default to True if no default is given'

    def test_envvar(self):
        p = Param(3).register('foo', None, breadcrumbs=[])
        assert p.envvar == 'FOO'
        p = Param(3).register('foo', 'app', breadcrumbs=[])
        assert p.envvar == 'APP_FOO'
        p = Param(3).register('foo', None, breadcrumbs=['bar', 'baz'])
        assert p.envvar == 'BAR_BAZ_FOO'
        p = Param(3).register('foo', 'app', breadcrumbs=['quux'])
        assert p.envvar == 'APP_QUUX_FOO'

    def test_read_handles_default_and_required(self):
        p = Param('bar').register('foo')
        assert p.read('')


class TestEnvSettings:

    def test_flat(self):
        settings = EnvSettings(
            foo=Param(bool),
            bar=Param(int),
            baz=Param(str, default='quux'),
        ).register('var')
        env = dict(
            VAR_FOO='True',
            VAR_BAR='8',
        )
        ns = settings.read(env)

        assert ns.foo is True
        assert ns.bar == 8
        assert ns.baz == 'quux'

    def test_nested(self):
        settings = EnvSettings(
            foo=Param(bool),
            nested=EnvSettings(
                bar=Param(int),
                baz=Param(str, default='jazzz'),
            ),
        ).register('app')
        env = dict(
            APP_FOO='1',
            APP_NESTED_BAR='8',
            APP_NESTED_BAZ='funkkk',
        )
        ns = settings.read(env)

        assert ns.foo is True
        assert ns.nested.bar == 8
        assert ns.nested.baz == 'funkkk'
