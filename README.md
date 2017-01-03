# superdiff

superdiff is a Python library for performing flexible diff checks. 

Flexibility options include:
- Ignoring case
- Ignoring different amounts of whitespace
- Ignoring whitespace completely

See the [documentation](http://superdiff.readthedocs.io/en/latest/) for more details about the options provided.

## Installation and Requirements
This library requires Python 3. For versions earlier than Python 3.5, you must install the [typing package](https://pypi.python.org/pypi/typing)

To install using pip: `pip install superdiff`

## Basic Usage
```
import superdiff

exact_match_diff = superdiff.Differ().compare('spam', 'SPAM')
print(list(exact_match_diff))  # Output: [('spam', 'SPAM')]

case_insensitive_diff = superdiff.Differ(ignore_case=True).compare('spam', 'SPAM')
print(list(case_insensitive_diff))  # Output: []
```
