#######################################
# IMPORTS
#######################################

import pytest
from Celeratas.lexer.Lexer import Lexer
import Celeratas.helper.tokens as toks

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
    ("x ", [toks.TT_IDENTIFIER, "x"]),
    ("x\t", [toks.TT_IDENTIFIER, "x"]),
    # Should create a tab
    ("\t", [toks.TT_TAB]),
    ("    ", [toks.TT_TAB]),
    # Check for invalid chars
    pytest.param(".", [], marks=pytest.mark.xfail),
    # Check for newlines
    (";", [toks.TT_NEWLINE]),
    ("\n", [toks.TT_NEWLINE]),
    # Test comments:
    ("#.;x", [toks.TT_IDENTIFIER, "x"]),
    # Test strings:
    ("\"x\"", [toks.TT_STRING, ["x"]]),
    # Test identifiers:
    ("x", [toks.TT_IDENTIFIER, "x"]),
    # Test ints and floats
    ("1", [toks.TT_INT, 1]),
    ("1.0", [toks.TT_FLOAT, 1.0]),
    # Test numerals - dont test invalid numerals because that is the fault of convert roman not the lexer
    ("IV", [toks.TT_NUMERAL, 4]),
    # Test Comparison Ops
    ("==", [toks.TT_EE]),
    ("!=", [toks.TT_NE]),
    (">", [toks.TT_GT]),
    ("<", [toks.TT_LT]),
    (">=", [toks.TT_GTE]),
    ("<=", [toks.TT_LTE]),
    # Test Binary Operators
    ("+", [toks.TT_PLUS]),
    ("-", [toks.TT_MINUS]),
    ("*", [toks.TT_MUL]),
    ("/", [toks.TT_DIV]),
    ("^", [toks.TT_POW]),
    # Test Parens
    ("(", [toks.TT_LPAREN]),
    (")", [toks.TT_RPAREN]),
    ("[", [toks.TT_LSQUARE]),
    ("]", [toks.TT_RSQUARE]),
    ("{", [toks.TT_LBRACE]),
    ("}", [toks.TT_RBRACE]),
    # Test Misc
    ("=", [toks.TT_EQ]),
    (":", [toks.TT_COLON]),
    (",", [toks.TT_COMMA]),
    ("->", [toks.TT_ARROW])
])
def test_lexer(test_input, expected):
    lexer = Lexer("<std_in>", test_input)
    tokens, error = lexer.make_tokens()

    assert error is None
    expected.append(toks.TT_EOF)

    assert tokens[0].type == expected[0]
    if tokens[0].value:
        assert tokens[0].value == expected[1]
