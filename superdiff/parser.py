import re
from typing import Sequence


class Parser:
    def __init__(self,
                 ignore_case=False,
                 ignore_inline_whitespace=False,
                 ignore_inline_whitespace_changes=False,
                 ignore_newline_changes=False,
                 ignore_blank_lines=False,
                 ignore_leading_whitespace=False,
                 ignore_trailing_whitespace=False):
        # NOTE: Make sure that this regex is applied before the general
        # whitespace one
        newline_chars = '\r|\r\n|\n'
        self._newline_regex = '({})'.format(newline_chars)
        if ignore_newline_changes:
            self._newline_regex += '+'

        if ignore_blank_lines:
            # To ignore blank lines, we capture zero or more newlines
            # and whitespace chars, ending with a newline.
            # The NewlineToken can then handle
            # the additional information as needed.
            self._newline_regex += '(({0}|[ \t])*{0})?'.format(newline_chars)

        self._whitespace_regex = '[ \t]'
        if ignore_inline_whitespace_changes:
            # One or more whitespace chars
            self._whitespace_regex += '+'

        # One or more non-whitespace chars.
        # NOTE: Make sure that the number regex is applied before this one
        self._word_regex = r'\S+'

        self._settings = self.Settings(
            ignore_case=ignore_case,
            ignore_inline_whitespace=ignore_inline_whitespace,
            ignore_inline_whitespace_changes=ignore_inline_whitespace_changes,
            ignore_newline_changes=ignore_newline_changes,
            ignore_blank_lines=ignore_blank_lines,
            ignore_leading_whitespace=ignore_leading_whitespace,
            ignore_trailing_whitespace=ignore_trailing_whitespace,
        )

    class Settings:
        # NOTE: we're only supporting \n \r and \r\n as newlines
        def __init__(self,
                     ignore_case=False,
                     ignore_inline_whitespace=False,
                     ignore_inline_whitespace_changes=False,
                     ignore_newline_changes=False,
                     ignore_blank_lines=False,
                     ignore_leading_whitespace=False,
                     ignore_trailing_whitespace=False):
            self.ignore_case = ignore_case
            self.ignore_inline_whitespace = ignore_inline_whitespace
            self.ignore_inline_whitespace_changes = ignore_inline_whitespace_changes
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

            if not isinstance(token, NewlineToken):
                continue

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
        return hash(self.transformed_text)


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

    # @property
    # def original_text(self) -> str:
    #     return

    def _get_transformed_text(self) -> str:
        if (self._settings.ignore_newline_changes or
                self._settings.ignore_blank_lines):
            return '\n'

        return super()._get_transformed_text()


class WhitespaceToken(Token):
    '''
    An InlineWhitespaceNode stores one or more non-newline whitespace
    characters (i.e. tabs and spaces).
    '''

    def _get_transformed_text(self):
        if self._settings.ignore_inline_whitespace:
            return ''

        if self._settings.ignore_inline_whitespace_changes:
            return ' '

        return super()._get_transformed_text()


def token_factory(token_type: str, regex_match, parser_settings):
    return _TOKEN_TYPES[token_type](regex_match, parser_settings)


_TOKEN_TYPES = {
    'word': WordToken,
    # 'number': NumberToken,
    'newline': NewlineToken,
    'whitespace': WhitespaceToken,
}


def main():
    text = '   SPAM \n\n\r\n egg  \t  sausage cheese \r\n \n    \n       \nbutts'
    p = Parser(ignore_blank_lines=False,
               ignore_case=False,
               ignore_leading_whitespace=False,
               ignore_trailing_whitespace=False,
               ignore_inline_whitespace_changes=False,
               ignore_inline_whitespace=False,
               ignore_newline_changes=True)
    lines = p.parse(text)

    for line in lines:
        # for token in line._tokens:
        #     print("'{}'".format(token.original_text))
        print(line.original_text)

    print('=' * 40)

    for line in lines:
        print(line.transformed_text)


if __name__ == '__main__':
    main()
