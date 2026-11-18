import pytest

from sloperator.errors import LexicalError
from sloperator.lexer import tokenize


@pytest.mark.parametrize(
    ("source", "line"),
    [
        ('— hi\n"', 2),
        ('— one\n— two\n— three\n"', 4),
        ('slop x = 1✨ — trailing\n"', 2),
    ],
)
def test_lexical_error_after_comment_reports_correct_line(source: str, line: int):
    with pytest.raises(LexicalError) as info:
        tokenize(source)
    assert info.value.line == line
    assert info.value.message == "straight quotes are not supported, use “ and ” for strings"
