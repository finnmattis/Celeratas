#######################################
# IMPORTS
#######################################

import Celeratas.helper.tokens as toks
import pytest
from Celeratas.lexer.Lexer import Lexer
from Celeratas.lexer.Token import Token

#######################################
# TESTS
#######################################


@pytest.mark.parametrize("test_input,expected,should_fail", [
    # Should be nothing
    ("", [], False),
    # Should throw error for improper tab - Tabs must either be 4 spaces or a tab unicode character
    (" ", [], True),
    # Should skip empty space bc it is after first grammatical char
    ("x ", [toks.TT_IDENTIFIER, "x"], False),
    ("x\t", [toks.TT_IDENTIFIER, "x"], False),
    # Should create a tab
    ("\t", [toks.TT_TAB], False),
    ("    ", [toks.TT_TAB], False),
    # Check for invalid chars
    ("~", [], True),
    # Check for newlines
    (";", [toks.TT_NEWLINE], False),
    ("\n", [toks.TT_NEWLINE], False),
    # Test comments:
    ("#.;x", [toks.TT_IDENTIFIER, "x"], False),
    # Test strings:
    ("\"x\"", [toks.TT_STRING, ["x"]], False),
    ("f\"x{1}x\"", [toks.TT_STRING, ["x", [Token(toks.TT_INT, 1), Token(toks.TT_EOF)], "x"]], False),
    ("\"x", [], True),
    # Test identifiers:
    ("x", [toks.TT_IDENTIFIER, "x"], False),
    # Test ints and floats
    ("1", [toks.TT_INT, 1], False),
    ("1.0", [toks.TT_FLOAT, 1.0], False),
    # Test numerals - dont test invalid numerals because that is the fault of convert roman not the lexer
    ("IV", [toks.TT_NUMERAL, 4], False),
    # Test Comparison Ops
    ("==", [toks.TT_EE], False),
    ("!=", [toks.TT_NE], False),
    (">", [toks.TT_GT], False),
    ("<", [toks.TT_LT], False),
    (">=", [toks.TT_GTE], False),
    ("<=", [toks.TT_LTE], False),
    # Test Binary Operators
    ("+", [toks.TT_PLUS], False),
    ("-", [toks.TT_MINUS], False),
    ("*", [toks.TT_MUL], False),
    ("/", [toks.TT_DIV], False),
    ("^", [toks.TT_POW], False),
    # Test Parens
    ("(", [toks.TT_LPAREN], False),
    (")", [toks.TT_RPAREN], False),
    ("[", [toks.TT_LSQUARE], False),
    ("]", [toks.TT_RSQUARE], False),
    ("{", [toks.TT_LBRACE], False),
    ("}", [toks.TT_RBRACE], False),
    # Test Misc
    ("=", [toks.TT_EQ], False),
    (":", [toks.TT_COLON], False),
    (",", [toks.TT_COMMA], False),
    ("=>", [toks.TT_ARROW], False)
])
def test_lexer(test_input, expected, should_fail):
    lexer = Lexer("<std_in>", test_input)
    tokens, error = lexer.make_tokens()

    if should_fail:
        assert error
    else:
        assert not error

        token = tokens[0]

        expected.append(toks.TT_EOF)
        assert token.type == expected[0]

        if len(test_input) > 0 and test_input[0] == "f":
            assert token.value[0] == expected[1][0]
            assert token.value[2] == expected[1][2]

            for i, e in zip(token.value[1], expected[1][1]):
                assert i.type == e.type
                assert i.value == e.value

        elif token.value:
            assert token.value == expected[1]
