from miscutils import functional as fx


class TestCurried:
    def test_args(self):
        def func(x, y):
            return x, y

        f = fx.curried(func)
        assert f() == fx.curried(func)
        f1 = f(1)
        assert f1 == fx.curried(func, 1)
        assert f1(2) == (1, 2)
        assert f1(2) == (1, 2)

        fy = f(y=2)
        assert fy(1) == (1, 2)

    def test_kws(self):
        def func(a=3, b=False, c="foo"):
            return a, b, c

        f = fx.curried(func)
        assert f() == (3, False, "foo")
        assert f(a=5) == (5, False, "foo")
        assert f(a=5, b=True) == (5, True, "foo")
        assert f(c="bar") == (3, False, "bar")
        assert f(a=5, c="bar") == (5, False, "bar")

    def test_args_kws(self):
        def func(x, y, a=3, b=False):
            return x, y, a, b

        f = fx.curried(func)
        assert f() == fx.curried(func)
        f1 = f(1)
        assert f1 == fx.curried(func, 1)
        assert f1(b=True) == fx.curried(func, 1, b=True)
        assert f1(2) == (1, 2, 3, False)
        assert f1(2, b=True) == (1, 2, 3, True)

        fbc = f(a=5, b=True)
        assert fbc == fx.curried(func, a=5, b=True)
        fbc1 = fbc(1)
        assert fbc1 == fx.curried(func, 1, a=5, b=True)
        assert fbc1(2) == (1, 2, 5, True)

    def test_kwonly(self):
        def func(x, y, a=3, b=False, *, c="foo", d=-0.5):
            return x, y, a, b, c, d

        f = fx.curried(func)
        assert f() == fx.curried(func)
        f1 = f(1)
        assert f1 == fx.curried(func, 1)
        assert f1(2) == (1, 2, 3, False, "foo", -0.5)
        assert f1(2, a=5) == (1, 2, 5, False, "foo", -0.5)
        assert f1(2, c="bar") == (1, 2, 3, False, "bar", -0.5)
        assert f1(2, c="bar", d=-1.5) == (1, 2, 3, False, "bar", -1.5)

        f1c = f1(c="bar")
        assert f1c == fx.curried(func, 1, c="bar")
        assert f1c(2) == (1, 2, 3, False, "bar", -0.5)
