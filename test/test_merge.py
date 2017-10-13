from utils.merge import merge




def test_merge_0():
    base = dict(x=1, y=2, z=3)
    dict1 = dict(x=1, y=4)
    result = merge(base, dict1)
    assert result == dict(x=1, y=4, z=3)


def test_merge_1():
    base = dict(x=1, y=2, z=3)
    dict1 = dict(x=1, y=4)
    dict2 = dict(x=8, z=5, a=11)
    result = merge(base, dict1, dict2)
    assert result == dict(x=8, y=4, z=5, a=11)


def test_merge_2():
    base = dict(x=1, y=2, z=3)
    dict1 = dict(y=4)
    kwargs = dict(z=9, a=5)
    result = merge (base, dict1, **kwargs)
    assert result == dict(x=1, y=4, z=9, a=5)
