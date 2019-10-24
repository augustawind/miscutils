from miscutils import iters


def test_cons():
    assert tuple(iters.cons(1, [2, 3])) == (1, 2, 3)
    assert list(iters.cons(1, (2, 3))) == [1, 2, 3]
    assert list(iters.cons(1, range(2, 4))) == [1, 2, 3]


def test_rcons():
    assert tuple(iters.rcons(1, [2, 3])) == (2, 3, 1)
    assert list(iters.rcons(1, (2, 3))) == [2, 3, 1]
    assert list(iters.rcons(1, range(2, 4))) == [2, 3, 1]


def test_insert():
    assert list(iters.insert(2, 11, range(0, 5))) == [0, 1, 11, 2, 3, 4]


def test_intersperse():
    assert ''.join(iters.intersperse('-', 'abcd')) == 'a-b-c-d'
