import pytest

from miscutils.merge import merge


def inits(seq):
    return (seq[: i + 1] for i in range(len(seq)))


class MergeTestBase:

    depth = 0
    base = NotImplemented
    dict1 = NotImplemented
    dict2 = NotImplemented
    kwargs = NotImplemented

    result_args_1 = NotImplemented
    result_args_2 = NotImplemented
    result_kwargs = NotImplemented
    result_args_1_kwargs = NotImplemented

    def test_args_1(self):
        assert self.result_args_1 == merge(
            self.base, self.dict1, _depth=self.depth
        )

    def test_args_2(self):
        assert self.result_args_2 == merge(
            self.base, self.dict1, self.dict2, _depth=self.depth
        )

    def test_kwargs(self):
        assert self.result_kwargs == merge(
            self.base, _depth=self.depth, **self.kwargs
        )

    def test_args_1_kwargs(self):
        assert self.result_args_1_kwargs == merge(
            self.base, self.dict1, _depth=self.depth, **self.kwargs
        )


class TestMerge(MergeTestBase):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.base = {"x": 1, "y": 2, "z": 3}
        self.dict1 = {"x": 1, "y": 4}
        self.dict2 = {"x": 8, "z": 5, "a": 11}
        self.kwargs = {"z": 9, "a": 5}

        self.args_groups = inits(
            (self.base, self.dict1, self.dict2, self.kwargs)
        )

        self.result_args_1 = {"x": 1, "y": 4, "z": 3}
        self.result_args_2 = {"x": 8, "y": 4, "z": 5, "a": 11}
        self.result_kwargs = {"x": 1, "y": 2, "z": 9, "a": 5}
        self.result_args_1_kwargs = {"x": 1, "y": 4, "z": 9, "a": 5}

        yield

    def test_base_new_dict_ok(self):
        for args in self.args_groups:
            assert (
                merge({}, *args) is not self.base
            ), f"base returned from merge(dict(), ...ARGS) where ARGS={args}"

    def test_same_object_returned(self):
        for args in self.args_groups:
            assert (
                merge(*args) is self.base
            ), f"base not returned from merge(BASE, ..ARGS) where ARGS={args}"


class MergeNestedTestBase(MergeTestBase):
    def setup(self):
        self.base = {"x": 1, "y": 2, "z": {"a": 9, "b": 8, "c": 7}}
        self.dict1 = {"x": 11, "z": {"b": {"b": {"c": 13}}}}
        self.dict2 = {"y": 12, "z": {"a": 19, "c": 17}, "a": {"a": 1}}
        self.kwargs = {"a": 19, "z": {"b": {"b": {"b": 18}}}}


class TestMergeNestedLimit0(MergeNestedTestBase):
    depth = 0

    @pytest.fixture(autouse=True)
    def setup(self):
        super().setup()
        self.result_args_1 = {"x": 11, "y": 2, "z": {"b": {"b": {"c": 13}}}}
        self.result_args_2 = {
            "x": 11,
            "y": 12,
            "z": {"a": 19, "c": 17},
            "a": {"a": 1},
        }
        self.result_kwargs = {
            "x": 1,
            "y": 2,
            "z": {"b": {"b": {"b": 18}}},
            "a": 19,
        }
        self.result_args_1_kwargs = {
            "x": 11,
            "y": 2,
            "z": {"b": {"b": {"b": 18}}},
            "a": 19,
        }
        yield


class TestMergeNestedUnlimited(MergeNestedTestBase):
    depth = -1

    @pytest.fixture(autouse=True)
    def setup(self):
        super().setup()
        self.result_args_1 = {
            "x": 11,
            "y": 2,
            "z": {"a": 9, "b": {"b": {"c": 13}}, "c": 7},
        }
        self.result_args_2 = {
            "x": 11,
            "y": 12,
            "z": {"a": 19, "b": {"b": {"c": 13}}, "c": 17},
            "a": {"a": 1},
        }
        self.result_kwargs = {
            "x": 1,
            "y": 2,
            "z": {"a": 9, "b": {"b": {"b": 18}}, "c": 7},
            "a": 19,
        }
        self.result_args_1_kwargs = {
            "x": 11,
            "y": 2,
            "z": {"a": 9, "b": {"b": {"b": 18, "c": 13}}, "c": 7},
            "a": 19,
        }
        yield
