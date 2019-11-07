import pytest

from miscutils.const import Const, ConstError


@pytest.fixture
def bug():
    class Bug(Const):
        SPIDER: str
        BEATLE: str
        WORM: str

    return Bug


def test_read(bug):
    assert bug.SPIDER == "spider"
    assert bug.BEATLE == "beatle"
    assert bug["WORM"] == "worm"
    assert bug.keys() == ("SPIDER", "BEATLE", "WORM")
    assert bug.values() == ("spider", "beatle", "worm")
    assert bug.items() == (
        ("SPIDER", "spider"),
        ("BEATLE", "beatle"),
        ("WORM", "worm"),
    )


def test_write(bug):
    with pytest.raises(ConstError):
        bug.SPIDER = "sss"
    with pytest.raises(ConstError):
        bug.FOO = "sss"
    with pytest.raises(TypeError):
        bug["SPIDER"] = "sss"
    with pytest.raises(TypeError):
        bug["FOO"] = "sss"
    with pytest.raises(ConstError):
        del bug.SPIDER
    with pytest.raises(TypeError):
        del bug["SPIDER"]


def test_default_factory():
    class Bug(Const):
        def default_factory(s):
            return "".join(reversed(s)).lower()

        SPIDER: str

    assert Bug.SPIDER == "redips"


def test_explicit_values():
    class Bug(Const):
        SPIDER: str = "Recluse"
        BEATLE: str

    assert Bug.SPIDER == "Recluse"
    assert Bug.BEATLE == "beatle"
    assert Bug["SPIDER"] == "Recluse"
    assert Bug.items() == (("SPIDER", "Recluse"), ("BEATLE", "beatle"))
