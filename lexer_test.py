from main.lexer import Lexer
from helper.tokens import *


def lexer_test(querry, expected_error, expected_length=None):
    lexer = Lexer("<std_in>", querry)
    tokens, error = lexer.make_tokens()

    if expected_error:
        assert error != None
    else:
        assert error == None

    if expected_length:
        assert len(tokens) == expected_length
    return tokens


def test_lexer_blank_space():

    # Should not create any tokens besides EOF
    tokens = lexer_test("", False, 1)
    assert tokens[0].type == TT_EOF

    # Should throw error for improper tab - Tabs must either be 4 spaces or a tab unicode character
    tokens = lexer_test(" ", True)

    # Should create only 2 tokens - Should skip empty space bc it is after first grammatical char
    tokens = lexer_test("_ ", False, 2)

    # Should create only 2 tokens - Should skip empty space bc it is after first grammatical char
    tokens = lexer_test("x\t", False, 2)

    # Should create TAB and EOF tokens
    tokens = lexer_test("    ", False, 2)
    assert tokens[0].type == TT_TAB

    # Should create TAB and EOF tokens
    tokens = lexer_test("\t", False, 2)
    assert tokens[0].type == TT_TAB


def test_lexer_invalid_chars():
    # Should throw an error
    tokens = lexer_test(".", True)


def test_lexer_lines():

    # Should create a new line token
    tokens = lexer_test(";", False, 2)
    assert tokens[0].type == TT_NEWLINE

    # Should create a new line
    tokens = lexer_test(";", False, 2)
    assert tokens[0].type == TT_NEWLINE


def test_lexer_comments():
    # Should not return error
    tokens = lexer_test("#.;1", False, 2)


def test_lexer_strings():
    # Should return a string token with a value of "x"
    tokens = lexer_test("\"x\"", False, 2)
    assert tokens[0].type == TT_STRING
    assert tokens[0].value == "x"


def test_lexer_identifiers():
    # Should return an identifier with a value of "x" and no idx_to_get
    tokens = lexer_test("x", False, 2)
    assert tokens[0].type == TT_IDENTIFIER
    assert tokens[0].value == "x"


def test_lexer_numbers():
    # Should return a int token with a value of 5
    tokens = lexer_test("5", False, 2)
    assert tokens[0].type == TT_INT
    assert tokens[0].value == 5

    # Should return a numeral token with a value of 4
    tokens = lexer_test("IV", False, 2)
    assert tokens[0].type == TT_NUMERAL
    assert tokens[0].value == 4


def test_lexer_comparison_ops():
    # Should return a equals token in the middle
    tokens = lexer_test("x == x", False, 4)
    assert tokens[1].type == TT_EE

    # Should return a not equals token in the middle
    tokens = lexer_test("x != x", False, 4)
    assert tokens[1].type == TT_NE

    # Should return a greater than token in the middle
    tokens = lexer_test("x > x", False, 4)
    assert tokens[1].type == TT_GT

    # Should return a less than token in the middle
    tokens = lexer_test("x < x", False, 4)
    assert tokens[1].type == TT_LT

    # Should return a great than equals token in the middle
    tokens = lexer_test("x >= x", False, 4)
    assert tokens[1].type == TT_GTE

    # Should return a less than equals token in the middle
    tokens = lexer_test("x <= x", False, 4)
    assert tokens[1].type == TT_LTE


def test_lexer_bin_op_toks():

    # Should return a plus token
    tokens = lexer_test("+", False, 2)
    assert tokens[0].type == TT_PLUS

    # Should return a minus token
    tokens = lexer_test("-", False, 2)
    assert tokens[0].type == TT_MINUS

    # Should return a mul token
    tokens = lexer_test("*", False, 2)
    assert tokens[0].type == TT_MUL

    # Should return a div token
    tokens = lexer_test("/", False, 2)
    assert tokens[0].type == TT_DIV

    # Should return a pow token
    tokens = lexer_test("^", False, 2)
    assert tokens[0].type == TT_POW


def test_lexer_paren():
    # Should return a RPAREN token
    tokens = lexer_test("(", False, 2)
    assert tokens[0].type == TT_LPAREN

    # Should return a LPAREN token
    tokens = lexer_test(")", False, 2)
    assert tokens[0].type == TT_RPAREN

    # Should return a LSQUARE token
    tokens = lexer_test("[", False, 2)
    assert tokens[0].type == TT_LSQUARE

    # Should return a RSQUARE token
    tokens = lexer_test("]", False, 2)
    assert tokens[0].type == TT_RSQUARE


def test_lexer_misc():
    # Should return a colon token
    tokens = lexer_test(":", False, 2)
    assert tokens[0].type == TT_COLON

    # Should return a comma token
    tokens = lexer_test(",", False, 2)
    assert tokens[0].type == TT_COMMA
