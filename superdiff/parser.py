from typing import IO, Iterable
import re


class TextTokenizer:
    def __init__(self,
                 # ignore_inline_whitespace=False,
                 ignore_inline_whitespace_changes=False):
                 # ignore_blank_lines=False,
                 # ignore_leading_whitespace=False,
                 # ignore_trailing_whitespace=False,
                 # number_comparison_precision=0):
                 # treat all line breaks as equal
                 # pass the flexibility settings into the tokens? into Line?
        '''
        Parameters:
        ignore_case -- TODO in differ

        # NOTE: tokenizer doesn't need this, but differ does
        # ignore_inline_whitespace -- When True, the tokenizer will still
        #     use non-newline whitespace to delimit words, but it will not
        #     add any InlineWhitespaceNodes to the generated tree.

        ignore_inline_whitespace_changes -- When True, the tokenizer will
            consume one or more non-newline whitespace characters when
            creating InlineWhitespaceNodes.

        # NOTE: push up to the differ
        # ignore_blank_lines -- When True, the tokenizer will ignore lines
        #     consisting entirely of whitespace characters.

        ignore_leading_whitespace -- ? in differ
        ignore_trailing_whitespace -- ? in differ

        number_comparison_precision -- A precision to use when comparing
            numeric values. When the values of two NumberNodes are
            compared, they will be considered equal if the absolute
            value of their difference is less than or equal to this
            value.
        '''
        # One or more non-whitespace chars
        self._word_regex = re.compile('\S+')
        if ignore_inline_whitespace_changes:
            # One or more whitespace chars
            self._whitespace_regex = re.compile(r'\s+')
        else:
            self._whitespace_regex = re.compile(r'\s')

        # self._number_regex = re.compile(
        #     r'-?'
        #     r'(\d+)|(\d*\.)'
        pass

    def tokenize(self, text: str) -> 'Iterable[Token]':
        pass


class Token:
    pass


# class Line:
#     '''
#     A Line consists of a
#     TODO
#     '''
#     def __init__(self, children=None):
#         if children is None:
#             self._children = []

#         self._children = children

#     @property
#     def children(self) -> Iterable[Token]:
#         return self._children

#     def add_children(self, *nodes: Token):
#         self._children += nodes


class WordToken(Token):
    '''
    A WordToken stores a string of non-whitespace characters.
    '''
    pass


class NumberToken(WordToken):
    '''
    A NumberToken stores a string of characters that make up an integer
    or floating point value.
    '''
    pass


class NewlineToken(Token):
    '''
    A NewlineNode stores one or more newline characters.
    '''
    pass


class WhitespaceToken(Token):
    '''
    An InlineWhitespaceNode stores one or more non-newline whitespace
    characters (i.e. tabs and spaces).
    '''
    pass


def token_factory(token_type: str, token_text: str) -> Token:
    return _TOKEN_TYPES[token_type](token_text)


_TOKEN_TYPES = {
    'word': WordToken,
    'number': NumberToken,
    'newline': NewlineToken,
    'whitespace': WhitespaceToken,
}
