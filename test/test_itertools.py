from utils import lists


def test_inits():
    assert tuple(lists.inits([1, 2, 3])) == ([1], [1, 2], [1, 2, 3])
    assert tuple(lists.inits((5, 4, 9))) == ((5,), (5, 4), (5, 4, 9))
    assert tuple(lists.inits('abc')) == ('a', 'ab', 'abc')


def test_tails():
    assert tuple(lists.tails([1, 2, 3])) == ([1, 2, 3], [1, 2], [1])
    assert tuple(lists.tails((5, 4, 9))) == ((5, 4, 9), (5, 4), (5,))
    assert tuple(lists.tails('abc')) == ('abc', 'ab', 'a')
