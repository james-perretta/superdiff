import unittest

from superdiff.differ import Differ


# Tests adapted from
# https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher.get_opcodes
class DifferTestCase(unittest.TestCase):
    def setUp(self):
        self.left_chars = ('q', 'a', 'b', 'x', 'c', 'd', 'e')
        self.right_chars = ('a', 'b', 'y', 'c', 'd', 'f', 'e')

    def test_texts_equal_default_options(self):
        text = 'spam egg sausage\nspam'
        diff = Differ().compare(text, text)
        self.assertEqual([], list(diff))

    def test_texts_equal_ignore_case(self):
        diff = Differ(ignore_case=True).compare('spam', 'SPam')
        self.assertEqual([], list(diff))

    def test_differ_defaults(self):
        left = '\n'.join(self.left_chars)
        right = '\n'.join(self.right_chars)
        diff = Differ().compare(left, right)

        expected = [
            ('delete',  'q\n', ''),
            ('equal',   'a\n', 'a\n'),
            ('equal',   'b\n', 'b\n'),
            ('replace', 'x\n', 'y\n'),
            ('equal',   'c\n', 'c\n'),
            ('equal',   'd\n', 'd\n'),
            ('insert',  '',    'f\n'),
            ('equal',   'e',   'e'),
        ]
        self.assertEqual(expected, list(diff))

    def test_differ_ignore_case(self):
        left = '\n'.join(char.upper() for char in self.left_chars)
        right = '\n'.join(self.right_chars)
        diff = Differ(ignore_case=True).compare(left, right)

        expected = [
            ('delete',  'Q\n', ''),
            ('equal',   'A\n', 'a\n'),
            ('equal',   'B\n', 'b\n'),
            ('replace', 'X\n', 'y\n'),
            ('equal',   'C\n', 'c\n'),
            ('equal',   'D\n', 'd\n'),
            ('insert',  '',    'f\n'),
            ('equal',   'E',   'e'),
        ]
        self.assertEqual(expected, list(diff))

    def test_differ_ignore_whitespace_changes(self):
        left = '\r\n'.join(char + ' \tSPAM' for char in self.left_chars)
        right = '\n'.join(char + ' SPAM' for char in self.right_chars)
        diff = Differ(ignore_non_newline_whitespace_changes=True,
                      ignore_newline_changes=True).compare(
            left, right
        )

        expected = [
            ('delete',  'q \tSPAM\r\n', ''),
            ('equal',   'a \tSPAM\r\n', 'a SPAM\n'),
            ('equal',   'b \tSPAM\r\n', 'b SPAM\n'),
            ('replace', 'x \tSPAM\r\n', 'y SPAM\n'),
            ('equal',   'c \tSPAM\r\n', 'c SPAM\n'),
            ('equal',   'd \tSPAM\r\n', 'd SPAM\n'),
            ('insert',  '',             'f SPAM\n'),
            ('equal',   'e \tSPAM',     'e SPAM'),
        ]
        self.assertEqual(expected, list(diff))

    def test_differ_ignore_whitespace_and_blank_lines(self):
        left = '\n \n'.join(char + ' \t' for char in self.left_chars)
        right = '\n'.join(self.right_chars)
        diff = Differ(ignore_non_newline_whitespace=True,
                      ignore_blank_lines=True).compare(left, right)

        expected = [
            ('delete',  'q \t\n \n', ''),
            ('equal',   'a \t\n \n', 'a\n'),
            ('equal',   'b \t\n \n', 'b\n'),
            ('replace', 'x \t\n \n', 'y\n'),
            ('equal',   'c \t\n \n', 'c\n'),
            ('equal',   'd \t\n \n', 'd\n'),
            ('insert',  '',          'f\n'),
            ('equal',   'e \t',      'e'),
        ]
        self.assertEqual(expected, list(diff))


if __name__ == '__main__':
    unittest.main()
