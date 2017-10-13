from utils import itertools as iters


def test_inits():
    assert tuple(iters.inits([1, 2, 3])) == ([1], [1, 2], [1, 2, 3])
    assert tuple(iters.inits((5, 4, 9))) == ((5,), (5, 4), (5, 4, 9))
    assert tuple(iters.inits('abc')) == ('a', 'ab', 'abc')


def test_tails():
    assert tuple(iters.tails([1, 2, 3])) == ([1, 2, 3], [1, 2], [1])
    assert tuple(iters.tails((5, 4, 9))) == ((5, 4, 9), (5, 4), (5,))
    assert tuple(iters.tails('abc')) == ('abc', 'ab', 'a')
