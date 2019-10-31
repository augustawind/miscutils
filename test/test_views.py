import copy

import pytest

from miscutils.views import DictView, SetView


class TestDictView:

    @pytest.fixture
    def d(self):
        if not hasattr(self, "__d"):
            self.__d = {0: "a", 1: "b", 2: "c", 3: "d"}
        return self.__d

    @pytest.fixture
    def dview(self, d):
        return DictView(d, (0, 2))

    def test_copy(self, dview):
        assert copy.copy(dview) == dview
        assert copy.deepcopy(dview) == dview

    def test_get(self, d, dview):
        # OK - access items in view
        assert dview[0] == "a"
        assert dview[2] == "c"

        # NOT OK - access items not in view
        with pytest.raises(KeyError):
            dview[1]
        with pytest.raises(KeyError):
            dview[3]
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
        with pytest.raises(KeyError):
            dview[1] == "B"

        d[2] = "C"
        assert dview[2] == "C"

    def test_del(self, d, dview):
        del dview[0]
        with pytest.raises(KeyError):
            d[0]
        del d[2]
        with pytest.raises(KeyError):
            dview[2]


class TestSetView:

    def test_copy(self):
        s = {"foo", "bar", "baz"}
        view = SetView(s, ("foo", "baz"))
        assert copy.copy(view) == view
        assert copy.deepcopy(view) == view
