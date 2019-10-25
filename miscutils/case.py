"""case - tools for parsing and formatting strings into various case styles"""
import re
from typing import List

from .classproperty import classproperty


class CaseStyle:
    """An abstract base class for strings in specific case styles.

    There are two sets of attributes that can be overridden on child classes
    to define behavior:

    - For parsing from a string:
      - **Must** define either ``WORD_PATTERN`` or ``parse``.
    - For converting into a string:
      - **Must** define either ``JOIN_BY`` + ``fmt_word`` or ``fmt``
      - ``fmt_word`` is not actually required, but by default it just returns
        its input. To customize output you will probably want to define
        ``fmt_word`` as well as ``JOIN_BY``.
    - Define ``fmt_1st_word`` if you defined ``fmt_word`` but you need the
      first word to be formatted differently than the rest. By default all
      words are formatted using ``fmt_word``.
    """

    def __init__(self, s: str):
        self._words = self.parse(s)
        assert len(self._words) > 0, \
            f'unable to parse str as {self.__class__.__name__}'

        self._cached__str__ = None

    def __str__(self):
        """Return a string representation of this ``CaseStyle``.

        You shouldn't need to override this. To customize display, override
        ``CaseStyle.fmt`` instead.
        """
        if not self._cached__str__:
            self._cached__str__ = self.fmt(self.words)
        return self._cached__str__

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

    def parse(self, s: str) -> List[str]:
        """Parse a string in this ``CaseStyle`` into a list of words.

        By default this uses ``self.WORD_PATTERN.findall`` to do this, so
        child classes must either define ``CaseStyle.WORD_PATTERN`` or
        override this method directly. In most cases, defining `WORD_PATTERN`
        should be enough.
        """
        return [
            ''.join(filter(bool, matches))
            for matches in self.WORD_PATTERN.findall(s)
        ]

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

    @classmethod
    def fmt(cls, words: List[str]) -> str:
        """Convert a list of words into a single string in this case style.

        By default this formats each word in ``words`` with
        ``cls.fmt_word``/``cls.fmt_1st_word`` and joins them with
        ``cls.JOIN_BY.join``. Child classes must define ``cls.JOIN_BY`` or
        override this method directly.

        Most child classes will probably want to override ``cls.fmt_word`` as
        well since the default just returns the word. If you need the first
        word to be formatted different from the rest, you can define
        ``cls.fmt_1st_word`` as well. If that still isn't sufficient you can
        just override this method.
        """
        return cls.JOIN_BY.join(
            (
                cls.fmt_1st_word(words[0]),
                *(cls.fmt_word(word) for word in words[1:])
            )
        )

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
    def fmt_1st_word(cls, word: str) -> str:
        """Convert a word into this case as the first word in the sequence.

        By default this just calls ``cls.fmt_word``, but it may be overridden
        if the first word should be formatted differently than the others.
        """
        return cls.fmt_word(word)

    @property
    def words(self) -> List[str]:
        """Return a copy of the list of words parsed by this ``CaseStyle``."""
        return self._words.copy()

    def to_case(self, case: 'CaseStyle') -> 'CaseStyle':
        """Convert this ``CaseStyle`` instance into another ``CaseStyle``."""
        return case(case.fmt(self.words))


class PascalCase(CaseStyle):
    """Represents a str in _PascalCase_."""

    WORD_PATTERN = re.compile(
        r"""
        (_* [A-Z] [a-z0-9_]*)
        """,
        re.VERBOSE,
    )
    JOIN_BY = ''

    @classmethod
    def fmt_word(cls, word):
        return word.title()


class CamelCase(CaseStyle):
    """Represents a str in _camelCase_."""

    WORD_PATTERN = re.compile(
        r"""
        \A (_* [a-z] [a-z0-9_]*)
            |
        ([A-Z] [a-z0-9_]*)
        """,
        re.VERBOSE,
    )
    JOIN_BY = ''

    @classmethod
    def fmt_1st_word(cls, word):
        return word.lower()

    @classmethod
    def fmt_word(cls, word):
        return word.title()


class SnakeCase(CaseStyle):
    """Represents a str in _snake_case_."""

    WORD_PATTERN = re.compile(
        r"""
        \A (_* [a-z] [a-z0-9]*)
            |
        ([a-z] [a-z0-9]*) (?:_+|\Z)
        """,
        re.VERBOSE,
    )
    JOIN_BY = '_'

    @classmethod
    def fmt_word(cls, word):
        return word.lower()


class KebabCase(CaseStyle):
    """Represents a str in _kebab-case_."""

    WORD_PATTERN = re.compile(
        r"""
        \A (_* [A-Za-z] [A-Za-z0-9_]*)
            |
        - ([A-Za-z] [A-Za-z0-9_]*)
        """,
        re.VERBOSE,
    )
    JOIN_BY = '-'

    @classmethod
    def fmt_word(cls, word):
        return word.lower()
