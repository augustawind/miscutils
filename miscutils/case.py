"""tools for parsing and formatting strings into various cases"""
import re
from typing import List

from .classproperty import classproperty

__all__ = ["CaseStyle", "CamelCase", "KebabCase", "PascalCase", "SnakeCase"]


class CaseStyle:
    """An abstract base class for strings in specific case styles.

    There are two sets of attributes that can be overridden on child classes
    to define behavior:

    For parsing *from* a case style:
        - Must define :attr:`WORD_PATTERN`.

    For converting *into* a case style:
        - Must define :attr:`SEPARATOR`, and you probably want to define
            :meth:`fmt_word` as well. By default it just returns its input.
        - You can also override :meth:`fmt`.
        - Define :meth:`fmt_1st_word` if you defined :meth:`fmt_word` but you
            need the first word to be formatted differently than the rest. By
            default all words are formatted using :meth:`fmt_word`.

    For more control over how text is parsed and formatted, you can override
    :meth:`parse` and :meth:`fmt` directly.
    """

    def __init__(self, s: str):
        self._words = self.parse(s)
        assert (
            len(self._words) > 0
        ), f"unable to parse str as {self.__class__.__name__}"

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
            "".join(filter(bool, matches))
            for matches in self.WORD_PATTERN.findall(s)
        ]

    @classproperty
    def SEPARATOR(cls) -> str:
        """The `str` that separates words in this ``CaseStyle``.

        It is used by the default implementation for ``cls.fmt`` to join the
        ``CaseStyle``'s words into a `str`. If ``cls.fmt`` is not overridden
        this must be defined, as a class-level attribute:

        >>> class SnakeCase(CaseStyle):
        ...     SEPARATOR = '_'
        ...     # ...snip...
        """
        raise NotImplementedError

    @classmethod
    def fmt(cls, words: List[str]) -> str:
        """Convert a list of words into a single string in this case style.

        By default this formats each word in ``words`` with
        ``cls.fmt_word``/``cls.fmt_1st_word`` and joins them with
        ``cls.SEPARATOR.join``. Child classes must define ``cls.SEPARATOR`` or
        override this method directly.

        Most child classes will probably want to override ``cls.fmt_word`` as
        well since the default just returns the word. If you need the first
        word to be formatted different from the rest, you can define
        ``cls.fmt_1st_word`` as well. If that still isn't sufficient you can
        just override this method.
        """
        return cls.SEPARATOR.join(
            (
                cls.fmt_1st_word(words[0]),
                *(cls.fmt_word(word) for word in words[1:]),
            )
        )

    @classmethod
    def fmt_word(cls, word: str) -> str:
        """Convert a word into this case style.

        By default this simply returns the given `word`. The default
        implementation for ``cls.fmt`` uses this method to format each word
        and joins them with ``cls.SEPARATOR``. Defining this method is
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

    def to_case(self, case: "CaseStyle") -> "CaseStyle":
        """Convert this ``CaseStyle`` instance into another ``CaseStyle``."""
        return case(case.fmt(self.words))


class PascalCase(CaseStyle):
    """Represents a str in ``PascalCase``."""

    WORD_PATTERN = re.compile(
        r"""
        (_* [A-Z] [a-z0-9_]*)
        """,
        re.VERBOSE,
    )
    SEPARATOR = ""

    @classmethod
    def fmt_word(cls, word):
        return word.title()


class CamelCase(CaseStyle):
    """Represents a str in ``camelCase``."""

    WORD_PATTERN = re.compile(
        r"""
        \A (_* [a-z] [a-z0-9_]*)
            |
        ([A-Z] [a-z0-9_]*)
        """,
        re.VERBOSE,
    )
    SEPARATOR = ""

    @classmethod
    def fmt_1st_word(cls, word):
        return word.lower()

    @classmethod
    def fmt_word(cls, word):
        return word.title()


class SnakeCase(CaseStyle):
    """Represents a str in ``snake_case``."""

    WORD_PATTERN = re.compile(
        r"""
        \A (_* [a-z] [a-z0-9]*)
            |
        ([a-z] [a-z0-9]*) (?:_+|\Z)
        """,
        re.VERBOSE,
    )
    SEPARATOR = "_"

    @classmethod
    def fmt_word(cls, word):
        return word.lower()


class KebabCase(CaseStyle):
    """Represents a str in ``kebab-case``."""

    WORD_PATTERN = re.compile(
        r"""
        \A (_* [A-Za-z] [A-Za-z0-9_]*)
            |
        - ([A-Za-z] [A-Za-z0-9_]*)
        """,
        re.VERBOSE,
    )
    SEPARATOR = "-"

    @classmethod
    def fmt_word(cls, word):
        return word.lower()
