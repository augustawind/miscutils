from utils.envparse import EnvSettings, Param


class TestParam:

    def test_always_required_if_no_default(self):
        param = Param('foo', required=False)
        assert param.required is True
        param = Param('foo', default=5, required=False)
        assert param.required is False


    def test_read_enforces_requires(self):
        pass


class TestEnvSettings:

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
        settings.read(env)

        assert settings.foo is True
        assert settings.nested.bar == 8
        assert settings.nested.baz == 'funkkk'
