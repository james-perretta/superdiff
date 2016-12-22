import unittest

from superdiff.differ import Differ


# Tests adapted from
# https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher.get_opcodes
class DifferTestCase(unittest.TestCase):
    def setUp(self):
        self.left_chars = ('q', 'a', 'b', 'x', 'c', 'd')
        self.right_chars = ('a', 'b', 'y', 'c', 'd', 'f')

    def test_differ_defaults(self):
        left = '\n'.join(self.left_chars)
        right = '\n'.join(self.right_chars)
        diff = Differ().compare(left, right)

        expected = [
            ('q\n', ''),
            ('a\n', 'a\n'),
            ('b\n', 'b\n'),
            ('x\n', 'y\n'),
            ('c\n', 'c\n'),
            ('d',   'd\n'),
            ('',    'f'),
        ]
        self.assertEqual(expected, list(diff))

    def test_differ_ignore_case(self):
        left = '\n'.join(char.upper() for char in self.left_chars)
        right = '\n'.join(self.right_chars)
        diff = Differ(ignore_case=True).compare(left, right)

        expected = [
            ('Q\n', ''),
            ('A\n', 'a\n'),
            ('B\n', 'b\n'),
            ('X\n', 'y\n'),
            ('C\n', 'c\n'),
            ('D',   'd\n'),
            ('',    'f'),
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
            ('q \tSPAM\r\n', ''),
            ('a \tSPAM\r\n', 'a SPAM\n'),
            ('b \tSPAM\r\n', 'b SPAM\n'),
            ('x \tSPAM\r\n', 'y SPAM\n'),
            ('c \tSPAM\r\n', 'c SPAM\n'),
            ('d \tSPAM',     'd SPAM\n'),
            ('',             'f SPAM'),
        ]
        self.assertEqual(expected, list(diff))

    def test_differ_ignore_whitespace_and_blank_lines(self):
        left = '\n \n'.join(char + ' \t' for char in self.left_chars)
        right = '\n'.join(self.right_chars)
        diff = Differ(ignore_non_newline_whitespace=True,
                      ignore_blank_lines=True).compare(left, right)

        expected = [
            ('q \t\n \n', ''),
            ('a \t\n \n', 'a\n'),
            ('b \t\n \n', 'b\n'),
            ('x \t\n \n', 'y\n'),
            ('c \t\n \n', 'c\n'),
            ('d \t',      'd\n'),
            ('',          'f'),
        ]
        self.assertEqual(expected, list(diff))


if __name__ == '__main__':
    unittest.main()
