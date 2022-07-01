#######################################
# IMPORTS
#######################################

import pytest

from Celeratas.helper.tokens import *

from Celeratas.lexer.Lexer import Lexer
from Celeratas.lexer.Position import Position
from Celeratas.lexer.Token import Token
from Celeratas.parser.Parser import Parser
from Celeratas.parser.nodes import *

#######################################
# TESTS
#######################################

basepos = Position(0, 0, 0, "<stdin>", "1")
# Use basepos because error location does not matter


def parser_test_base(test_input):
    lexer = Lexer("<std_in>", test_input)
    tokens, _ = lexer.make_tokens()

    parser = Parser(tokens)
    ast = parser.parse()

    assert ast.error == None
    return ast.node.element_nodes[0]


@pytest.mark.parametrize("test_input,expected", [
    ("1", NumberNode(Token(TT_INT, 1, basepos))),
    ("IV", NumeralNode(Token(TT_NUMERAL, 4, basepos))),
    pytest.param("\"x", [], marks=pytest.mark.xfail),
])
def test_parser_numbers(test_input, expected):
    ast = parser_test_base(test_input)
    assert ast.tok.value == expected.tok.value


@pytest.mark.parametrize("test_input,expected", [
    ("\"x\"", StringNode(["x"], basepos, basepos)),
    ("f\"{1}\"", StringNode(
        [NumberNode(Token(TT_INT, 1, basepos))], basepos, basepos))
])
def test_parser_strings(test_input, expected):
    ast = parser_test_base(test_input)
    for i, e in zip(ast.str_components, expected.str_components):
        if hasattr(i, "tok"):
            assert i.tok.value == e.tok.value
        else:
            assert i == e


@pytest.mark.parametrize("test_input,expected", [
    (("-1", UnaryOpNode(Token(TT_MINUS, pos_start=basepos),
     NumberNode(Token(TT_INT, 1, basepos))))),
    (("+1", UnaryOpNode(Token(TT_PLUS, pos_start=basepos),
     NumberNode(Token(TT_INT, 1, basepos)))))
])
def test_parser_un_op(test_input, expected):
    ast = parser_test_base(test_input)
    assert ast.op_tok.type == expected.op_tok.type
    assert ast.node.tok.value == expected.node.tok.value


@pytest.mark.parametrize("test_input,expected", [
    ("1+1", BinOpNode(NumberNode(Token(TT_INT, 1, basepos)),
     Token(TT_PLUS, pos_start=basepos), NumberNode(Token(TT_INT, 1, basepos)))),
])
def test_parser_bin_op(test_input, expected):
    ast = parser_test_base(test_input)

    assert ast.op_tok.type == expected.op_tok.type
    assert ast.left_node.tok.value == expected.left_node.tok.value
    assert ast.right_node.tok.value == expected.right_node.tok.value


@pytest.mark.parametrize("test_input,expected", [
    ("[1, 2, 3]", ListNode(element_nodes=[NumberNode(Token(TT_INT, 1, basepos)), NumberNode(
        Token(TT_INT, 2, basepos)), NumberNode(Token(TT_INT, 3, basepos))], pos_start=basepos, pos_end=basepos)),
    pytest.param("[x = 10]", [], marks=pytest.mark.xfail),
])
def test_parser_list(test_input, expected):
    ast = parser_test_base(test_input)
    for (out_el, exp_out_el) in zip(ast.element_nodes, expected.element_nodes):
        assert out_el.tok.value == exp_out_el.tok.value


@pytest.mark.parametrize("test_input,expected", [
    ("x", VarAccessNode(Token(TT_IDENTIFIER, "x", basepos,), [], None)),
    ("x[0]", VarAccessNode(Token(TT_IDENTIFIER, "x", basepos),
                           [NumberNode(Token(TT_INT, 0, basepos))], None)),
    ("x[0][0]", VarAccessNode(Token(TT_IDENTIFIER, "x", basepos),
                              [NumberNode(Token(TT_INT, 0, basepos)), NumberNode(Token(TT_INT, 0, basepos))], None)),
])
def test_parser_var_access(test_input, expected):
    ast = parser_test_base(test_input)
    assert ast.var_name_tok.value == expected.var_name_tok.value
    for out_idx, exp_out_idx in zip(ast.idxes_to_get, expected.idxes_to_get):
        assert out_idx.tok.value == exp_out_idx.tok.value


@pytest.mark.parametrize("test_input,expected", [
    ("x = 1", VarAssignNode(Token(TT_IDENTIFIER, "x", basepos),
                            NumberNode(Token(TT_INT, 1, basepos)), [], Token(TT_EQ, basepos))),
    ("x[0] = 1", VarAssignNode(Token(TT_IDENTIFIER, "x", basepos),
                               NumberNode(Token(TT_INT, 1, basepos)), [NumberNode(Token(TT_INT, 0, basepos))], Token(TT_EQ, basepos))),

])
def test_parser_var_assign(test_input, expected):
    ast = parser_test_base(test_input)
    assert ast.var_name_tok.value == expected.var_name_tok.value
    assert ast.value_node.tok.value == expected.value_node.tok.value
    for out_idx, exp_out_idx in zip(ast.idxes_to_change, expected.idxes_to_change):
        assert out_idx.tok.value == exp_out_idx.tok.value


@pytest.mark.parametrize("test_input,expected", [
    ("si 1 == 1:;    1", [])
])
def test_parser_if(test_input, expected):
    ast = parser_test_base(test_input)
    case = ast.cases[0]
