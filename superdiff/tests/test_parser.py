import unittest

from superdiff.parser import Parser


class _Base:
    def _check_transformed_lines(self, expected_lines, lines, original_text):
        print(expected_lines)
        print([line.transformed_text for line in lines])
        self.assertEqual(len(expected_lines), len(lines))
        for expected, line in zip(expected_lines, lines):
            self.assertEqual(expected, line.transformed_text)

        self.assertEqual(original_text, ''.join(line.original_text for line in lines))


class ParserMiscSettingsComboTestCase(_Base, unittest.TestCase):
    def setUp(self):
        self.original_lines = (
            '\tspam egg  SAUSAGE\tspam   \n',
            '  \r\n',
            '\r',
            'WALUIGI\twuluigio    \t')
        self.text = ''.join(self.original_lines)

    def test_no_filters(self):
        parser = Parser()
        lines = parser.parse(self.text)
        self._check_transformed_lines(self.original_lines, lines, self.text)

    def test_ignore_all_whitespace_changes(self):
        parser = Parser(
            ignore_non_newline_whitespace_changes=True,
            ignore_newline_changes=True
        )
        lines = parser.parse(self.text)
        expected_lines = [
            ' spam egg SAUSAGE spam \n',
            ' \n',
            '\n',
            'WALUIGI wuluigio '
        ]
        self._check_transformed_lines(expected_lines, lines, self.text)

    def test_ignore_all_whitespace_changes_and_blank_lines(self):
        parser = Parser(
            ignore_non_newline_whitespace_changes=True,
            ignore_newline_changes=True,
            ignore_blank_lines=True
        )
        lines = parser.parse(self.text)
        expected_lines = [
            ' spam egg SAUSAGE spam \n',
            'WALUIGI wuluigio '
        ]
        self._check_transformed_lines(expected_lines, lines, self.text)

    def test_all_ignores_enabled(self):
        parser = Parser(
            ignore_case=True,
            ignore_non_newline_whitespace=True,
            ignore_non_newline_whitespace_changes=True,
            ignore_newline_changes=True,
            ignore_blank_lines=True,
            ignore_leading_whitespace=True,
            ignore_trailing_whitespace=True
        )
        lines = parser.parse(self.text)
        expected_lines = [
            'spam egg sausage spam',
            '',
            '',
            'waluigi wuluigio'
        ]
        self._check_transformed_lines(expected_lines, lines, self.text)


class ParserMiscSettingsTestCase(_Base, unittest.TestCase):
    def test_ignore_case(self):
        parser = Parser(ignore_case=True)
        text = 'SPAMeggSAUSAGEspam'
        lines = parser.parse(text)

        self.assertEqual(1, len(lines))
        line = lines[0]
        self.assertEqual(text.lower(), line.transformed_text)

    def test_ignore_non_newline_whitespace(self):
        parser = Parser(ignore_non_newline_whitespace=True)
        text = 'spam egg    \nsausage\t  \t spam'
        lines = parser.parse(text)
        expected_lines = [
            'spamegg\n',
            'sausagespam'
        ]
        self._check_transformed_lines(expected_lines, lines, text)

    def test_ignore_non_newline_whitespace_changes(self):
        parser = Parser(ignore_non_newline_whitespace_changes=True)
        text = 'spam   egg\t  \t\n  \t sausage spam\t\n'
        lines = parser.parse(text)
        expected_lines = [
            'spam egg \n',
            ' sausage spam \n'
        ]
        self._check_transformed_lines(expected_lines, lines, text)

    def test_ignore_non_newline_whitespace_overrides_ignore_non_newline_whitespace_changes(self):
        parser = Parser(ignore_non_newline_whitespace_changes=True,
                        ignore_non_newline_whitespace=True)
        text = 'spam   egg\t  \t\n  \t sausage spam\t\n'
        lines = parser.parse(text)
        expected_lines = [
            'spamegg\n',
            'sausagespam\n'
        ]
        self._check_transformed_lines(expected_lines, lines, text)

    def test_ignore_newline_changes(self):
        parser = Parser(ignore_newline_changes=True)
        text = 'spam\negg\rsausage\r\n'
        lines = parser.parse(text)
        expected_lines = [
            'spam\n',
            'egg\n',
            'sausage\n'
        ]
        self._check_transformed_lines(expected_lines, lines, text)


class LeadingAndTrailingWhitespaceTestCase(_Base, unittest.TestCase):
    def setUp(self):
        self.text = (' \t spam egg\t \n'
                     'sausage \t\n'
                     ' \t\n')

    def test_ignore_leading_whitespace(self):
        parser = Parser(ignore_leading_whitespace=True)
        lines = parser.parse(self.text)
        expected_lines = [
            'spam egg\t \n',
            'sausage \t\n',
            ''
        ]
        self._check_transformed_lines(expected_lines, lines, self.text)

    def test_ignore_trailing_whitespace(self):
        parser = Parser(ignore_trailing_whitespace=True)
        lines = parser.parse(self.text)
        expected_lines = [
            ' \t spam egg',
            'sausage',
            ''
        ]
        self._check_transformed_lines(expected_lines, lines, self.text)

    def test_ignore_leading_and_trailing_whitespace(self):
        parser = Parser(ignore_leading_whitespace=True,
                        ignore_trailing_whitespace=True)
        lines = parser.parse(self.text)
        expected_lines = [
            'spam egg',
            'sausage',
            ''
        ]
        self._check_transformed_lines(expected_lines, lines, self.text)


class ParserBlankLineSettingsTestCase(_Base, unittest.TestCase):
    def setUp(self):
        self.text = ('spam\n  \r'
                     'egg\n    \r\n'
                     'sausage\r\n  \r'
                     'cheese\r\n \n'
                     'waluigi\r \t \r\n'
                     'stove\n \n'
                     'stave\r \r'
                     'stuve\r\n\r\n \t ')

    def test_ignore_blank_lines(self):
        parser = Parser(ignore_blank_lines=True)
        lines = parser.parse(self.text)
        expected_lines = [
            'spam\n',
            'egg\n',
            'sausage\r\n',
            'cheese\r\n',
            'waluigi\r',
            'stove\n',
            'stave\r',
            'stuve\r\n'
            # ' \t '
        ]
        self._check_transformed_lines(expected_lines, lines, self.text)

    def test_ignore_newline_changes_and_blank_lines(self):
        parser = Parser(ignore_blank_lines=True, ignore_newline_changes=True)
        lines = parser.parse(self.text)
        expected_lines = [
            'spam\n',
            'egg\n',
            'sausage\n',
            'cheese\n',
            'waluigi\n',
            'stove\n',
            'stave\n',
            'stuve\n'
            # ' \t '
        ]
        self._check_transformed_lines(expected_lines, lines, self.text)


if __name__ == '__main__':
    unittest.main()
