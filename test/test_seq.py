from utils import seq


def test_inits():
    assert tuple(seq.inits([1, 2, 3])) == ([1], [1, 2], [1, 2, 3])
    assert tuple(seq.inits((5, 4, 9))) == ((5,), (5, 4), (5, 4, 9))
    assert tuple(seq.inits('abc')) == ('a', 'ab', 'abc')


def test_tails():
    assert tuple(seq.tails([1, 2, 3])) == ([1, 2, 3], [1, 2], [1])
    assert tuple(seq.tails((5, 4, 9))) == ((5, 4, 9), (5, 4), (5,))
    assert tuple(seq.tails('abc')) == ('abc', 'ab', 'a')


def test_cons():
    assert tuple(seq.cons(1, [2, 3])) == (1, 2, 3)
    assert list(seq.cons(1, (2, 3))) == [1, 2, 3]
    assert list(seq.cons(1, range(2, 4))) == [1, 2, 3]


def test_rcons():
    assert tuple(seq.rcons(1, [2, 3])) == (2, 3, 1)
    assert list(seq.rcons(1, (2, 3))) == [2, 3, 1]
    assert list(seq.rcons(1, range(2, 4))) == [2, 3, 1]


def test_insert():
    assert list(seq.insert(2, 11, range(0, 5))) == [0, 1, 11, 2, 3, 4]


def test_intersperse():
    assert ''.join(seq.intersperse('-', 'abcd')) == 'a-b-c-d'
