#######################################
# IMPORTS
#######################################

import pytest
from Celeratas.lexer.Lexer import Lexer
from Celeratas.helper.tokens import *

#######################################
# TESTS
#######################################

# TODO f-string test


@pytest.mark.parametrize("test_input,expected", [
    # Should be nothing
    ("", []),
    # Should throw error for improper tab - Tabs must either be 4 spaces or a tab unicode character
    pytest.param(" ", [], marks=pytest.mark.xfail),
    # Should skip empty space bc it is after first grammatical char
    ("x ", [TT_IDENTIFIER, "x"]),
    ("x\t", [TT_IDENTIFIER, "x"]),
    # Should create a tab
    ("\t", [TT_TAB]),
    ("    ", [TT_TAB]),
    # Check for invalid chars
    pytest.param(".", [], marks=pytest.mark.xfail),
    # Check for newlines
    (";", [TT_NEWLINE]),
    ("\n", [TT_NEWLINE]),
    # Test comments:
    ("#.;x", [TT_IDENTIFIER, "x"]),
    # Test strings:
    ("\"x\"", [TT_STRING, ["x"]]),
    # Test identifiers:
    ("x", [TT_IDENTIFIER, "x"]),
    # Test ints and floats
    ("1", [TT_INT, 1]),
    ("1.0", [TT_FLOAT, 1.0]),
    # Test numerals - dont test invalid numerals because that is the fault of convert roman not the lexer
    ("IV", [TT_NUMERAL, 4]),
    # Test Comparison Ops
    ("==", [TT_EE]),
    ("!=", [TT_NE]),
    (">", [TT_GT]),
    ("<", [TT_LT]),
    (">=", [TT_GTE]),
    ("<=", [TT_LTE]),
    # Test Binary Operators
    ("+", [TT_PLUS]),
    ("-", [TT_MINUS]),
    ("*", [TT_MUL]),
    ("/", [TT_DIV]),
    ("^", [TT_POW]),
    # Test Parens
    ("(", [TT_LPAREN]),
    (")", [TT_RPAREN]),
    ("[", [TT_LSQUARE]),
    ("]", [TT_RSQUARE]),
    ("{", [TT_LBRACE]),
    ("}", [TT_RBRACE]),
    # Test Misc
    ("=", [TT_EQ]),
    (":", [TT_COLON]),
    (",", [TT_COMMA]),
    ("->", [TT_ARROW])
])
def test_lexer(test_input, expected):
    lexer = Lexer("<std_in>", test_input)
    tokens, error = lexer.make_tokens()

    assert error == None
    expected.append(TT_EOF)

    assert tokens[0].type == expected[0]
    if tokens[0].value:
        assert tokens[0].value == expected[1]
