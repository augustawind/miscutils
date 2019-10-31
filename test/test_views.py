import copy

import pytest

from miscutils.views import DictView, SetView


class TestDictView:
    @pytest.fixture
    def d(self):
        if not hasattr(self, "__d"):
            self.__d = {0: "a", 1: "b", 2: "c", "foo": "bar"}
        return self.__d

    @pytest.fixture
    def dview(self, d):
        return DictView(d, (0, 2))

    def test_copy(self, dview):
        assert copy.copy(dview) == dview
        assert copy.deepcopy(dview) == dview

    def test_keys_values_items(self, dview):
        assert set(dview.keys()) == {0, 2}
        assert set(dview.values()) == {"a", "c"}
        assert set(dview.items()) == {(0, "a"), (2, "c")}

    def test_get(self, d, dview):
        # OK - access items in view
        assert dview[0] == "a"
        assert dview[2] == "c"

        # NOT OK - access items not in view
        with pytest.raises(KeyError):
            dview[1]
        with pytest.raises(KeyError):
            dview["foo"]
        with pytest.raises(KeyError):
            dview[4]

        # can't access item in view if deleted from dict
        del d[0]
        with pytest.raises(KeyError):
            d[0]

        # if item changed in dict, item also changed in view
        d[2] = "C"
        assert dview[2] == "C"

    def test_set(self, d, dview):
        dview[0] = "A"
        assert d[0] == "A"
        dview[1] = "B"
        assert d[1] == "B"
        dview[8] = "foo"
        assert d[8] == "foo"

        d[2] = "C"
        assert dview[2] == "C"

    def test_del(self, d, dview):
        del dview[0]
        with pytest.raises(KeyError):
            d[0]
        del d[2]
        with pytest.raises(KeyError):
            dview[2]

    def test_bulk_ops(self, d, dview):
        dview.update(foo="biff")
        assert d == {0: "a", 1: "b", 2: "c", "foo": "biff"}
        dview.update(baz="quux")
        assert d == {0: "a", 1: "b", 2: "c", "foo": "biff", "baz": "quux"}

        dview.clear()
        assert dview == {}
        assert d == {1: "b"}


class TestSetView:
    @pytest.fixture
    def s(self):
        if not hasattr(self, "__s"):
            self.__s = {"foo", "bar", "baz", "quux"}
        return self.__s

    @pytest.fixture
    def sview(self, s):
        return SetView(s, ("foo", "baz"))

    def test_copy(self, sview):
        assert copy.copy(sview) == sview
        assert copy.deepcopy(sview) == sview

    def test_contains(self, s, sview):
        assert "foo" in sview
        assert "baz" in sview
        assert "bar" not in sview
        assert "quux" not in sview

    def test_add_rm(self, s, sview):
        sview.add("biff")
        assert "biff" in s
        sview.remove("biff")
        assert "biff" not in s
        sview.remove("foo")
        assert "foo" not in s
        with pytest.raises(KeyError):
            sview.remove("bar")
        assert s == {"bar", "baz", "quux"}
        sview.clear()
        assert s == {"bar", "quux"}

    def test_set_ops(self, s, sview: SetView):
        # disjoint
        assert sview.isdisjoint({"bah", "bum"})

        # subset/superset
        s2 = set(sview)
        assert sview <= s2
        assert sview >= s2
        assert not sview < s2
        assert not sview > s2
        assert sview < s
        assert sview > {"foo"}

        # union
        s2 = {"bar", "biff"}
        assert sview | s2 == SetView(s, ("foo", "baz", "bar"))
        assert sview | s2 == SetView(s, ("foo", "baz", "bar"))

        # intersection
        s2 = {"baz", "biff"}
        assert sview & s2 == SetView(s, ("baz",))
        assert s2 & sview == {"baz"}

        # difference
        s2 = {"baz", "biff"}
        assert sview - s2 == SetView(s, ("foo",))
        assert s2 - sview == SetView(s, ())

        # symmetric difference
        s2 = {"baz", "quux", "biff"}
        assert sview ^ s2 == SetView(s, ("foo", "quux"))
        assert s2 ^ sview == SetView(s, ("foo", "quux"))

    def test_update(self, s, sview):
        init_s = copy.copy(s)
        sview |= {"bar", "biff"}
        assert sview == SetView(s, ("foo", "baz", "bar"))
        assert s == init_s

    def test_intersection_update(self, s, sview):
        init_s = copy.copy(s)
        sview &= {"baz", "biff"}
        assert sview == SetView(s, ("baz",))
        assert s == init_s

    def test_difference_update(self, s, sview):
        init_s = copy.copy(s)
        sview -= {"baz", "biff"}
        assert sview == SetView(s, ("foo",))
        assert s == init_s

    def test_symmetric_difference_update(self, s, sview):
        init_s = copy.copy(s)
        sview ^= {"baz", "quux", "biff"}
        assert sview == SetView(s, ("foo", "quux"))
        assert s == init_s