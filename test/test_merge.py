import pytest

from utils.merge import merge


class Base:

    base = NotImplemented
    dict1 = NotImplemented
    dict2 = NotImplemented
    kwargs = NotImplemented

    result_args_1 = NotImplemented
    result_args_2 = NotImplemented
    result_kwargs = NotImplemented
    result_args_1_kwargs = NotImplemented

    def test_args_1(self, z=1):
        assert self.result_args_1 == \
            merge(self.base, self.dict1, _depth=z)

    def test_args_2(self, z=1):
        assert self.result_args_2 == \
            merge(self.base, self.dict1, self.dict2, _depth=z)

    def test_kwargs(self, z=1):
        assert self.result_kwargs == \
            merge(self.base, _depth=z, **self.kwargs)

    def test_args_1_kwargs(self, z=1):
        assert self.result_args_1_kwargs == \
            merge(self.base, self.dict1, _depth=z, **self.kwargs)


class TestMergeBasic(Base):

    @pytest.fixture(autouse=True)
    def setup(self):
        self.base = {'x': 1, 'y': 2, 'z': 3}
        self.dict1 = {'x': 1, 'y': 4}
        self.dict2 = {'x': 8, 'z': 5, 'a': 11}
        self.kwargs = {'z': 9, 'a': 5}

        self.result_args_1 = {'x': 1, 'y': 4, 'z': 3}
        self.result_args_2 = {'x': 8, 'y': 4, 'z': 5, 'a': 11}
        self.result_kwargs = {'x': 1, 'y': 2, 'z': 9, 'a': 5}
        self.result_args_1_kwargs = {'x': 1, 'y': 4, 'z': 9, 'a': 5}

        yield


class TestMergeDicts(Base):

    @pytest.fixture(autouse=True)
    def setup(self):
        self.base = {'x': 1,
                     'y': 2,
                     'z': {'a': 9, 'b': 8, 'c': 7}}
        self.dict1 = {'x': 11,
                      'z': {'c': 17}}
        self.dict2 = {'y': 12,
                      'z': {'a': 19, 'c': 17},
                      'a': {'a': 1}}
        self.kwargs = {'a': 19,
                       'z': {'b': {'b': {'b': 18}}}}

        self.result_args_1 = {'x': 11,
                              'y': 2,
                              'z': {'a': 9, 'b': 8, 'c': 17}}
        self.result_args_2 = {'x': 11,
                              'y': 12,
                              'z': {'a': 19, 'b': 8, 'c': 17},
                              'a': {'a': 1}}
        self.result_kwargs = {'x': 1,
                              'y': 2,
                              'z': {'a': 9, 'b': {'b': {'b': 18}}, 'c': 7},
                              'a': 19}
        self.result_args_1_kwargs = {'x': 11,
                                     'y': 2,
                                     'z': {'a': 9, 'b': {'b': {'b': 18}},
                                           'c': 17},
                                     'a': 19}
