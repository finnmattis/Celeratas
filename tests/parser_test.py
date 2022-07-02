#######################################
# IMPORTS
#######################################

import pytest

import Celeratas.helper.tokens as toks

from Celeratas.lexer.Lexer import Lexer
from Celeratas.lexer.Position import Position
from Celeratas.lexer.Token import Token
from Celeratas.parser.Parser import Parser
from Celeratas.parser.nodes import NumberNode, NumeralNode, StringNode, ListNode, VarAccessNode, BinOpNode, UnaryOpNode, VarAssignNode

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

    assert ast.error is None
    return ast.node.element_nodes[0]


@pytest.mark.parametrize("test_input,expected", [
    ("1", NumberNode(1, basepos, basepos)),
    ("IV", NumeralNode(4, basepos, basepos)),
    pytest.param("\"x", [], marks=pytest.mark.xfail),
])
def test_parser_numbers(test_input, expected):
    ast = parser_test_base(test_input)
    assert ast.value == expected.value


@pytest.mark.parametrize("test_input,expected", [
    ("\"x\"", StringNode(["x"], basepos, basepos)),
    ("f\"{1}\"", StringNode(
        [NumberNode(1, basepos, basepos)], basepos, basepos))
])
def test_parser_strings(test_input, expected):
    ast = parser_test_base(test_input)
    for i, e in zip(ast.str_components, expected.str_components):
        if hasattr(i, "value"):
            assert i.value == e.value
        else:
            assert i == e


@pytest.mark.parametrize("test_input,expected", [
    (("-1", UnaryOpNode(Token(toks.TT_MINUS, pos_start=basepos),
     NumberNode(1, basepos, basepos), basepos, basepos))),
    (("+1", UnaryOpNode(Token(toks.TT_PLUS, pos_start=basepos),
     NumberNode(1, basepos, basepos), basepos, basepos)))
])
def test_parser_un_op(test_input, expected):
    ast = parser_test_base(test_input)
    assert ast.op_tok.type == expected.op_tok.type
    assert ast.node.value == expected.node.value


@pytest.mark.parametrize("test_input,expected", [
    ("1+1", BinOpNode(NumberNode(1, basepos, basepos),
     Token(toks.TT_PLUS, basepos), NumberNode(1, basepos, basepos), basepos, basepos))
])
def test_parser_bin_op(test_input, expected):
    ast = parser_test_base(test_input)

    assert ast.op_tok.type == expected.op_tok.type
    assert ast.left_node.value == expected.left_node.value
    assert ast.right_node.value == expected.right_node.value


@pytest.mark.parametrize("test_input,expected", [
    ("[1, 2, 3]", ListNode([NumberNode(1, basepos, basepos), NumberNode(
        2, basepos, basepos), NumberNode(3, basepos, basepos)], basepos, basepos)),
    pytest.param("[x = 10]", [], marks=pytest.mark.xfail),
])
def test_parser_list(test_input, expected):
    ast = parser_test_base(test_input)
    for i, e in zip(ast.element_nodes, expected.element_nodes):
        assert i.value == e.value


@pytest.mark.parametrize("test_input,expected", [
    ("x", VarAccessNode("x", [], None, basepos, basepos)),
    ("x[0]", VarAccessNode("x", [NumberNode(0, basepos, basepos)], None, basepos, basepos)),
    ("x[0][0]", VarAccessNode("x", [NumberNode(0, basepos, basepos), NumberNode(0, basepos, basepos)], None, basepos, basepos)),
    ("x.attr", VarAccessNode("x", [], "attr", basepos, basepos)),
    ("x[0].attr", VarAccessNode("x", [NumberNode(0, basepos, basepos)], "attr", basepos, basepos)),
])
def test_parser_var_access(test_input, expected):
    ast = parser_test_base(test_input)
    assert ast.var_name_to_get == expected.var_name_to_get
    assert ast.attr_to_get == expected.attr_to_get
    for out_idx, exp_out_idx in zip(ast.idxes_to_get, expected.idxes_to_get):
        assert out_idx.value == exp_out_idx.value


@pytest.mark.parametrize("test_input,expected", [
    ("x = 1", VarAssignNode([["x", []]], [NumberNode(1, basepos, basepos)], Token(toks.TT_EQ, basepos), basepos, basepos)),
    ("x[0] = 1", VarAssignNode([["x", [NumberNode(0, basepos, basepos)]]], [NumberNode(1, basepos, basepos)], Token(toks.TT_EQ, basepos), basepos, basepos)),

])
def test_parser_var_assign(test_input, expected):
    ast = parser_test_base(test_input)

    assert ast.vars_to_set[0][0] == expected.vars_to_set[0][0]
    for i, e in zip(ast.vars_to_set[0][1], expected.vars_to_set[0][1]):
        assert i.value == e.value
    for i, e in zip(ast.values_to_set, expected.values_to_set):
        assert i.value == e.value
    assert ast.assign_type.type == expected.assign_type.type
