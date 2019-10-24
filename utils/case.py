import abc
import re
from typing import List, Type


class CaseStyle(metaclass=abc.ABCMeta):

    WORD_PATTERN = re.compile('')

    @classmethod
    @abc.abstractmethod
    def fmt(cls, words: List[str]) -> str:
        pass

    @classmethod
    def words(cls, string: str) -> List[str]:
        return cls.WORD_PATTERN.findall(string)

    @classmethod
    def from_case(cls, case: Type['CaseStyle'], s: str):
        return cls.fmt(case.words(s))


class CamelCase(CaseStyle):

    WORD_PATTERN = re.compile(r'(?:\A[a-z_]|[A-Z_])[a-z0-9_]*')

    @classmethod
    def fmt(cls, words: List[str]) -> str:
        return words[0].lower() + ''.join(word.title() for word in words[1:])


class SnakeCase(CaseStyle):

    WORD_PATTERN = re.compile(r'(?:\A|_)(_*[A-Za-z0-9]+)')

    @classmethod
    def fmt(cls, words: List[str]) -> str:
        return '_'.join(word.lower() for word in words)


class KebabCase(CaseStyle):

    WORD_PATTERN = re.compile(r'(?:\A|-)(-*[A-Za-z0-9_]+)')

    @classmethod
    def fmt(cls, words: List[str]) -> str:
        return '-'.join(word.lower() for word in words)
