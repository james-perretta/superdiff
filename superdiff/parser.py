import re
from typing import Sequence


_NEWLINE_CHARS = r'(\r\n)|(\r)|(\n)'  # KEEP THESE IN ORDER
_NEWLINE_THEN_WHITESPACE = r'({newline}|[ \t])*'.format(newline=_NEWLINE_CHARS)


class Parser:
    def __init__(self,
                 ignore_case=False,
                 ignore_non_newline_whitespace=False,
                 ignore_non_newline_whitespace_changes=False,
                 ignore_newline_changes=False,
                 ignore_blank_lines=False,
                 ignore_leading_whitespace=False,
                 ignore_trailing_whitespace=False):
        self._newline_regex = '({})'.format(_NEWLINE_CHARS)
        if ignore_newline_changes:
            self._newline_regex += '+'

        if ignore_blank_lines:
            # When ignoring blank lines, we match any of the
            # following (in order):
            #   1. A 'newline sandwich' (any amount or kind of
            #      whitespace surrounded by 2 newlines) followed
            #      optionally by any amount of non-newline whitespace
            #      and the end of the string.
            #   2. A single newline char
            self._newline_regex = (
                r'({newline})({newline_then_whitespace})({newline})(([ \t]*$)?)|'
                '({newline})').format(newline=_NEWLINE_CHARS,
                                      newline_then_whitespace=_NEWLINE_THEN_WHITESPACE)

        self._whitespace_regex = '[ \t]'
        if ignore_non_newline_whitespace_changes:
            # One or more whitespace chars
            self._whitespace_regex += '+'

        # One or more non-whitespace chars.
        self._word_regex = r'\S+'

        self._settings = self.Settings(
            ignore_case=ignore_case,
            ignore_non_newline_whitespace=ignore_non_newline_whitespace,
            ignore_non_newline_whitespace_changes=ignore_non_newline_whitespace_changes,
            ignore_newline_changes=ignore_newline_changes,
            ignore_blank_lines=ignore_blank_lines,
            ignore_leading_whitespace=ignore_leading_whitespace,
            ignore_trailing_whitespace=ignore_trailing_whitespace,
        )

    class Settings:
        # NOTE: we're only supporting \n \r and \r\n as newlines
        def __init__(self,
                     ignore_case=False,
                     ignore_non_newline_whitespace=False,
                     ignore_non_newline_whitespace_changes=False,
                     ignore_newline_changes=False,
                     ignore_blank_lines=False,
                     ignore_leading_whitespace=False,
                     ignore_trailing_whitespace=False):
            self.ignore_case = ignore_case
            self.ignore_non_newline_whitespace = ignore_non_newline_whitespace
            self.ignore_non_newline_whitespace_changes = ignore_non_newline_whitespace_changes
            self.ignore_newline_changes = ignore_newline_changes
            self.ignore_blank_lines = ignore_blank_lines
            self.ignore_leading_whitespace = ignore_leading_whitespace
            self.ignore_trailing_whitespace = ignore_trailing_whitespace

    def _get_token_spec(self) -> Sequence[tuple]:
        return [
            # IMPORTANT: DO NOT CHANGE THE ORDER OF THESE!!!!
            ('newline', self._newline_regex),
            ('whitespace', self._whitespace_regex),
            ('word', self._word_regex)
        ]

    def parse(self, text: str) -> Sequence['Line']:
        lines = []

        token_regex = '|'.join(
            '(?P<{0}>{1})'.format(token_type, regex)
            for token_type, regex in self._get_token_spec())

        tokens = []
        for match in re.finditer(token_regex, text):
            token = token_factory(match.lastgroup, match, self._settings)
            tokens.append(token)

            if isinstance(token, NewlineToken) or match.end() == len(text):
                lines.append(Line(tokens, self._settings))
                tokens = []

        return lines


class Line:
    '''
    A line consists of a series of Tokens, with the final token being
    a NewlineToken.
    '''

    def __init__(self, tokens: Sequence['Token'], settings: Parser.Settings) -> None:
        self._tokens = tokens
        self._settings = settings
        self._hash = None  # type: int

    @property
    def transformed_text(self) -> str:
        text = ''.join(token.transformed_text for token in self._tokens)

        if (self._settings.ignore_leading_whitespace and
                self._settings.ignore_trailing_whitespace):
            text = text.strip()
        elif self._settings.ignore_leading_whitespace:
            text = text.lstrip()
        elif self._settings.ignore_trailing_whitespace:
            text = text.rstrip()

        return text

    @property
    def original_text(self) -> str:
        return ''.join(token.original_text for token in self._tokens)

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(self.transformed_text)

        return self._hash

    def __eq__(self, other):
        if not isinstance(other, Line):
            return False

        return hash(self) == hash(other)

    def __str__(self):
        return self.original_text


class Token:
    def __init__(self, regex_match, settings: Parser.Settings) -> None:
        self._regex_match = regex_match
        self._text = self._get_matched_text()
        self._settings = settings
        self._transformed_text = None  # type: str

    def _get_matched_text(self) -> str:
        return self._regex_match.group()

    @property
    def original_text(self) -> str:
        return self._text

    @property
    def transformed_text(self) -> str:
        if self._transformed_text is None:
            self._transformed_text = self._get_transformed_text()

        return self._transformed_text

    def _get_transformed_text(self) -> str:
        return self._text


class WordToken(Token):
    '''
    A WordToken stores a string of non-whitespace characters.
    '''

    def _get_transformed_text(self) -> str:
        text = self._text
        if self._settings.ignore_case:
            text = text.lower()

        return text


class NewlineToken(Token):
    '''
    A NewlineNode stores one or more newline characters.
    '''

    def __init__(self, regex_match, settings: Parser.Settings) -> None:
        super().__init__(regex_match, settings)

    def _get_transformed_text(self) -> str:
        if self._settings.ignore_newline_changes:
            return '\n'

        if self._settings.ignore_blank_lines:
            return re.match(_NEWLINE_CHARS, self._text).group()

        return super()._get_transformed_text()


class WhitespaceToken(Token):
    '''
    An InlineWhitespaceNode stores one or more non-newline whitespace
    characters (i.e. tabs and spaces).
    '''

    def _get_transformed_text(self):
        if self._settings.ignore_non_newline_whitespace:
            return ''

        if self._settings.ignore_non_newline_whitespace_changes:
            return ' '

        return super()._get_transformed_text()


def token_factory(token_type: str, regex_match, parser_settings) -> Token:
    '''
    Instantiates a token of the specified type.
    '''
    return _TOKEN_TYPES[token_type](regex_match, parser_settings)


_TOKEN_TYPES = {
    'word': WordToken,
    'newline': NewlineToken,
    'whitespace': WhitespaceToken,
}
