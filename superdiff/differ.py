import difflib
import itertools
from typing import Iterable, Tuple

from .parser import Parser


class Differ:
    r'''
    This class can be used to flexibly compare two pieces of text and
    return diff information in a variety of formats.

    Definitions of common terms used:

    - non-newline whitespace: Tabs and spaces
    - newline: Any of the following line endings: ``\n``, ``\r``, or
      ``\r\n``
    - whitespace: A combination of newlines and non-newline whitespace
    - empty line: A line consisting of only whitespace

    '''

    def __init__(self,
                 ignore_case: bool=False,
                 ignore_non_newline_whitespace: bool=False,
                 ignore_non_newline_whitespace_changes: bool=False,
                 ignore_newline_changes: bool=False,
                 ignore_blank_lines: bool=False,
                 ignore_leading_whitespace: bool=False,
                 ignore_trailing_whitespace: bool=False) -> None:
        r'''
        :param ignore_case: Ignore case differences between the two
            texts.
        :param ignore_non_newline_whitespace: Completely ignore
            differences in non-newline whitespace.
        :param ignore_non_newline_whitespace_changes: Treat consecutive
            sequences of non-newline whitespace as equal.
            For example, when this option is True, a single
            space, two spaces, a tab character, and a mix of tabs and
            spaces will be considered equal.
        :param ignore_newline_changes: Treat consecutive sequences of
            newline characters as equal. For example, when this option
            is True, ``\r``, ``\r\r\n``, and ``\n\n`` will all be
            considered equal.
        :param ignore_blank_lines: Ignore lines consisting of only
            whitespace.
        :param ignore_leading_whitespace: Ignore whitespace characters
            at the beginning of lines. Note that this will cause empty
            lines to be treated as the empty string.
        :param ignore_trailing_whitespace: Ignore whitespace characters
            at the end of lines. Note that this will cause empty
            lines to be treated as the empty string.
        '''
        self._parser = Parser(
            ignore_case=ignore_case,
            ignore_non_newline_whitespace=ignore_non_newline_whitespace,
            ignore_non_newline_whitespace_changes=ignore_non_newline_whitespace_changes,
            ignore_newline_changes=ignore_newline_changes,
            ignore_blank_lines=ignore_blank_lines,
            ignore_leading_whitespace=ignore_leading_whitespace,
            ignore_trailing_whitespace=ignore_trailing_whitespace
        )

    def compare(self, first: str, second: str) -> Iterable[Tuple[str, str]]:
        '''
        Performs a line-by-line comparision of the strings first and
        second and returns a sequence of pairs specifying the
        differences between the strings.

        If the two strings are equal, returns an empty sequence.

        Although this format results in some duplicated information in
        the case of exact matches, we use it for the following reasons:

        #. When flexibility settings are turned on, first and
           second may contain different text even if they are
           considered equal.
        #. Displaying a side-by-side diff from this format is
           simpler than restoring from a list of deltas.

        '''
        result = tuple()  # type: Iterable[Tuple[str, str]]
        parsed_first = self._parser.parse(first)
        parsed_second = self._parser.parse(second)
        matcher = difflib.SequenceMatcher(a=parsed_first, b=parsed_second)

        sequences_equal = True

        for tag, first_start, first_end, second_start, second_end in matcher.get_opcodes():
            if tag != 'equal':
                sequences_equal = False

            pairs = itertools.zip_longest(
                (line.original_text for line in parsed_first[first_start:first_end]),
                (line.original_text for line in parsed_second[second_start:second_end]),
                fillvalue='')
            result = itertools.chain(result, pairs)

        if sequences_equal:
            return tuple()

        return result
