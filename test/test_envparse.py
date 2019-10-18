import pytest

from utils.envparse import (
    EnvSettings,
    InvalidParam,
    InvalidValue,
    MissingValue,
    Param,
)


class TestParam:

    def test_validation(self):
        with pytest.raises(
            InvalidParam,
            match='bar.baz.foo',
            message='should not permit required=True with a default',
        ):
            Param(int, default=5, required=True).register(
                'foo', breadcrumbs=['bar', 'baz']
            )

        with pytest.raises(
            InvalidParam,
            match='baz.foo',
            message='should ensure `default` is an instance of `type`',
        ):
            Param(int, default='x').register('foo', breadcrumbs=['baz'])

        p = Param(int, required=False).register('foo', breadcrumbs=[])
        assert p.required is False, \
            'required=False should be allowed with no default'
        assert p.default is None, \
            'default should default to None'

        p = Param(int, default=5, required=False).register('foo', [])
        assert p.required is False, \
            'required=False should be allowed with a default'

        p = Param(int, default=5).register('foo', [])
        assert p.required is False, \
            'required should default to False if a default is given'

        p = Param(int).register('foo', [])
        assert p.required is True, \
            'required should default to True if no default is given'
        assert p.default is None, \
            'default should default to None'

    def test_envvar(self):
        p = Param(int).register('foo', breadcrumbs=[])
        assert p.envvar == 'FOO'
        p = Param(int).register('foo', breadcrumbs=['app'])
        assert p.envvar == 'APP_FOO'
        p = Param(int).register('foo', breadcrumbs=['bar', 'baz'])
        assert p.envvar == 'BAR_BAZ_FOO'
        p = Param(int).register('foo', breadcrumbs=['app', 'quux'])
        assert p.envvar == 'APP_QUUX_FOO'

    def test_read_handles_default_and_required(self):
        with pytest.raises(
            MissingValue,
            match='APP_BAR_FOO',
            message='empty input should raise an error if no default',
        ):
            Param(int).register('foo', ['app', 'bar']).read({})

        p = Param(int, default=3).register('foo', [])
        assert p.read({}) == 3, \
            'empty input should use the provided default'

        p = Param(int, required=False).register('foo', [])
        assert p.read({}) == None, \
            'if required is False but no default is given, use None'


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
                biff=EnvSettings(
                    quux=Param(float),
                ),
            ),
        ).register('app')
        env = dict(
            APP_FOO='1',
            APP_NESTED_BAR='8',
            APP_NESTED_BIFF_QUUX='3.2',
        )
        ns = settings.read(env)

        assert ns.foo is True
        assert ns.nested.bar == 8
        assert ns.nested.baz == 'jazzz'
        assert ns.nested.biff.quux == 3.2
