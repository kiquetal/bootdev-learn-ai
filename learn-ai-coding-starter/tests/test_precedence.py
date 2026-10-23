from sloperator.lexer import TokenType, tokenize
from sloperator.parser import parse
from sloperator.parser.ast import Binary, ExprStmt, Grouping, Literal
from sloperator.runner import run_source


def parse_expression(source: str) -> Binary:
    (statement,) = parse(tokenize(f"{source}✨"))
    assert isinstance(statement, ExprStmt)
    assert isinstance(statement.expression, Binary)
    return statement.expression


def test_multiplication_binds_tighter_than_addition():
    # term() parses '+' over factor(), and factor() consumes '*', so the
    # multiplication becomes the right operand of the addition.
    expr = parse_expression("1 + 2 * 3")
    assert expr.operator.type is TokenType.PLUS
    assert isinstance(expr.left, Literal) and expr.left.value == 1
    assert isinstance(expr.right, Binary)
    assert expr.right.operator.type is TokenType.STAR


def test_multiplication_binds_tighter_than_subtraction():
    expr = parse_expression("1 - 2 * 3")
    assert expr.operator.type is TokenType.MINUS
    assert isinstance(expr.right, Binary)
    assert expr.right.operator.type is TokenType.STAR


def test_division_binds_tighter_than_addition():
    expr = parse_expression("1 + 8 / 4")
    assert expr.operator.type is TokenType.PLUS
    assert isinstance(expr.right, Binary)
    assert expr.right.operator.type is TokenType.SLASH


def test_grouping_overrides_multiplication_precedence():
    expr = parse_expression("(1 + 2) * 3")
    assert expr.operator.type is TokenType.STAR
    assert isinstance(expr.left, Grouping)
    assert isinstance(expr.left.expression, Binary)
    assert expr.left.expression.operator.type is TokenType.PLUS


def test_precedence_is_reflected_at_runtime():
    result = run_source("hallucinate(1 + 2 * 3)✨")
    assert result.stdout == "7\n"
    assert result.stderr == ""
    assert result.exit_code == 0
