from miscutils import functional as fx


class TestCurried:

    @staticmethod
    def f_args(x, y):
        return x, y

    @staticmethod
    def f_kws(a=3, b=False, c='foo'):
        return a, b, c

    @staticmethod
    def f_args_kws(x, y, a=3, b=False):
        return x, y, a, b

    @staticmethod
    def f_kwonly(x, y, a=3, b=False, *, c='foo', d=-0.5):
        return x, y, a, b, c, d

    def test_args(self):
        f = fx.Curried(self.f_args)
        f = f()
        assert f == fx.Curried(self.f_args)

        f1 = f(1)
        assert f1 == fx.Curried(self.f_args, 1)
        assert f1(2) == (1, 2)
        assert f1(2) == (1, 2)