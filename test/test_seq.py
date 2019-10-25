from miscutils import seq


def test_split():
    assert seq.split(2, (1, 2, 3, 4, 5)) == ((1, 2), (3, 4, 5))


def test_inits():
    assert tuple(seq.inits([1, 2, 3])) == ([1], [1, 2], [1, 2, 3])
    assert tuple(seq.inits((5, 4, 9))) == ((5,), (5, 4), (5, 4, 9))
    assert tuple(seq.inits("abc")) == ("a", "ab", "abc")


def test_tails():
    assert tuple(seq.tails([1, 2, 3])) == ([1, 2, 3], [1, 2], [1])
    assert tuple(seq.tails((5, 4, 9))) == ((5, 4, 9), (5, 4), (5,))
    assert tuple(seq.tails("abc")) == ("abc", "ab", "a")
