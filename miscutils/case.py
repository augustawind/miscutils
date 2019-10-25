"""case - tools for parsing and formatting strings into various case styles"""
import re
from typing import List

from .classproperty import classproperty


class CaseStyle:
    """An abstract base class for strings in specific case styles.

    Two sets of attributes/methods must be defined on child classes to be
    complete:

    - Either ``WORD_PATTERN``; or ``parse``.
    - Either ``JOIN_BY`` and ``fmt_word``; or ``fmt``.
    """

    def __init__(self, s: str):
        self._words = self.parse(s)
        assert len(self._words) > 0, \
            f'could not parse str as case {self.__class__.__name__}'

    @classproperty
    def WORD_PATTERN(cls) -> re.Pattern:
        """A ``re.Pattern`` that matches a single word in this ``CaseStyle``.

        It is used by the default implementation for ``cls.parse`` to parse a
        `str` into a list of words. If ``cls.parse`` is not overridden this
        must be defined, as a class-level attribute:

        >>> class Alphabetic(CaseStyle):
        ...     WORD_PATTERN = re.compile(r'[A-Za-z]')
        ...     # ...snip...
        """
        raise NotImplementedError

    @classproperty
    def JOIN_BY(cls) -> str:
        """The `str` that separates words in this ``CaseStyle``.

        It is used by the default implementation for ``cls.fmt`` to join the
        ``CaseStyle``'s words into a `str`. If ``cls.fmt`` is not overridden
        this must be defined, as a class-level attribute:

        >>> class SnakeCase(CaseStyle):
        ...     JOIN_BY = '_'
        ...     # ...snip...
        """
        raise NotImplementedError

    @property
    def words(self) -> List[str]:
        """Return a copy of the list of words parsed by this ``CaseStyle``."""
        return self._words.copy()

    def to_case(self, case: 'CaseStyle') -> 'CaseStyle':
        """Convert this ``CaseStyle`` instance into another ``CaseStyle``."""
        return case(case.fmt(self.words))

    def __str__(self):
        """Return a string representation of this CaseStyle.

        You shouldn't override this. To customize how this ``CaseStyle`` is
        displayed, override ``CaseStyle.fmt`` instead.
        """
        return self.fmt(self.words)

    def parse(self, s: str):
        """Parse a string in this CaseStyle into a list of words.

        By default this uses ``re.Pattern``'s `findall` method on
        ``CaseStyle.WORD_PATTERN``, which is a ``re.Pattern`` instance. For
        custom behavior just override this method instead of `WORD_PATTERN`.
        """
        return self.WORD_PATTERN.findall(s)

    @classmethod
    def fmt_1st_word(cls, word: str) -> str:
        """Convert a word into this case as the first word in the sequence.

        By default this just calls ``cls.fmt_word``, but it may be overridden
        if the first word should be formatted differently than the others.
        """
        return cls.fmt_word(word)

    @classmethod
    def fmt_word(cls, word: str) -> str:
        """Convert a word into this case style.

        By default this simply returns the given `word`. The default
        implementation for ``cls.fmt`` uses this method to format each word
        and joins them with ``cls.JOIN_BY``. Defining this method is
        the simplest way to customize how the ``CaseStyle`` is displayed.
        """
        return word

    @classmethod
    def fmt(cls, words: List[str]) -> str:
        """Convert a list of words into a single string in this case style.

        By default this formats each word in ``words`` with ``cls.fmt_word``
        and joins them with ``cls.JOIN_BY``. In most cases, defining
        those two attributes is simpler and provides sufficient customization
        for how this ``CaseStyle`` is displayed, but if you need more control
        you can just customize this method.
        """
        return cls.JOIN_BY.join(
            (
                cls.fmt_1st_word(words[0]),
                *(cls.fmt_word(word) for word in words[1:])
            )
        )


class CamelCase(CaseStyle):
    """Represents a str in _CamelCase_."""

    WORD_PATTERN = re.compile(r'(?:\A[a-z_]|[A-Z_])[a-z0-9_]*')
    JOIN_BY = ''

    @classmethod
    def fmt_1st_word(cls, word):
        return word.lower()

    @classmethod
    def fmt_word(cls, word):
        return word.title()


class SnakeCase(CaseStyle):
    """Represents a str in _snake_case_."""

    WORD_PATTERN = re.compile(r'(?:\A|_)(_*[A-Za-z0-9]+)')
    JOIN_BY = '_'

    @classmethod
    def fmt_word(cls, word):
        return word.lower()


class KebabCase(CaseStyle):
    """Represents a str in _kebab-case_."""

    WORD_PATTERN = re.compile(r'(?:\A|-)(-*[A-Za-z0-9_]+)')
    JOIN_BY = '-'

    @classmethod
    def fmt_word(cls, word):
        return word.lower()
