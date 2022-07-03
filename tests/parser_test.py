#######################################
# IMPORTS
#######################################

import pytest

import Celeratas.helper.tokens as toks

from Celeratas.lexer.Lexer import Lexer
from Celeratas.lexer.Position import Position
from Celeratas.lexer.Token import Token
from Celeratas.parser.Parser import Parser
from Celeratas.parser.nodes import BreakNode, CallNode, ContinueNode, ForNode, FuncDefNode, IfNode, NumberNode, NumeralNode, ReturnNode, StringNode, ListNode, TryNode
from Celeratas.parser.nodes import VarAccessNode, BinOpNode, UnaryOpNode, VarAssignNode, WhileNode

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
    ("x += 1", VarAssignNode([["x", []]], [NumberNode(1, basepos, basepos)], Token(toks.TT_PLUS_EQ, basepos), basepos, basepos)),
    ("x[0] = 1", VarAssignNode([["x", [NumberNode(0, basepos, basepos)]]], [NumberNode(1, basepos, basepos)], Token(toks.TT_EQ, basepos), basepos, basepos)),
    ("a, b = 1, 2", VarAssignNode([["a", []], ["b", []]], [NumberNode(1, basepos, basepos),
     NumberNode(2, basepos, basepos)], Token(toks.TT_EQ, basepos), basepos, basepos)),

])
def test_parser_var_assign(test_input, expected):
    ast = parser_test_base(test_input)

    assert ast.vars_to_set[0][0] == expected.vars_to_set[0][0]
    for i, e in zip(ast.vars_to_set[0][1], expected.vars_to_set[0][1]):
        assert i.value == e.value
    for i, e in zip(ast.values_to_set, expected.values_to_set):
        assert i.value == e.value
    assert ast.assign_type.type == expected.assign_type.type


@pytest.mark.parametrize("test_input,expected", [
    ("si 1: 1", IfNode([(NumberNode(1, basepos, basepos), NumberNode(1, basepos, basepos), False)], None, basepos, basepos)),
    ("si 1:;    1", IfNode([(NumberNode(1, basepos, basepos), ListNode([NumberNode(1, basepos, basepos)], basepos, basepos), True)], None, basepos, basepos)
     ),
    ("si 1:;    1;alioquin:;    1", IfNode([(NumberNode(1, basepos, basepos), ListNode([NumberNode(1, basepos, basepos), True],
     basepos, basepos), True)], (ListNode([NumberNode(1, basepos, basepos)], basepos, basepos), True), basepos, basepos)),
    ("si 1:;    1;alioquinsi 1:;    1", IfNode([(NumberNode(1, basepos, basepos), ListNode([NumberNode(1, basepos, basepos)], basepos, basepos), True),
                                                (NumberNode(1, basepos, basepos), ListNode([NumberNode(1, basepos, basepos)], basepos, basepos), True), basepos, basepos], None, basepos, basepos)),
    ("si 1:;    1;alioquinsi 1:;    1;alioquin:;    1", IfNode([(NumberNode(1, basepos, basepos), ListNode([NumberNode(1, basepos, basepos)], basepos, basepos), True),
                                                                (NumberNode(1, basepos, basepos), ListNode(
                                                                    [NumberNode(1, basepos, basepos)], basepos, basepos), True),
                                                                basepos, basepos], (ListNode([NumberNode(1, basepos, basepos)], basepos, basepos), True), basepos, basepos)),

])
def test_parser_if_node(test_input, expected):
    ast = parser_test_base(test_input)

    for idx, _ in enumerate(ast.cases):
        assert ast.cases[idx][0].value == expected.cases[idx][0].value
        assert ast.cases[idx][2] == expected.cases[idx][2]
        if ast.cases[idx][2]:
            for i, e in zip(ast.cases[idx][1].element_nodes, expected.cases[idx][1].element_nodes):
                assert i.value == e.value
        else:
            assert ast.cases[idx][1].value == expected.cases[idx][1].value

    if ast.else_case:
        assert ast.else_case[1] == expected.else_case[1]

        for i, e in zip(ast.else_case[0].element_nodes, expected.else_case[0].element_nodes):
            assert i.value == e.value


body = ListNode([NumberNode(1, basepos, basepos)], basepos, basepos)


@ pytest.mark.parametrize("test_input,expected", [
    ("tempta:    1", TryNode(NumberNode(1, basepos, basepos), None, None, None, False, basepos, basepos)),
    ("tempta:;    1", TryNode(body, None, None, None, True, basepos, basepos)),
    ("tempta:;    1;praeter:;    1", TryNode(body, body, None, None, True, basepos, basepos)),
    ("tempta:;    1;praeter Exception:;    1", TryNode(body, body, Token(toks.TT_IDENTIFIER, "Exception"), None, True, basepos, basepos)),
    ("tempta:;    1;praeter Exception tam e:;    1;", TryNode(body, body, Token(toks.TT_IDENTIFIER, "Exception"), Token(toks.TT_IDENTIFIER, "e"), True, basepos, basepos)),
])
def test_parser_try_node(test_input, expected):
    ast = parser_test_base(test_input)

    assert ast.should_return_null == expected.should_return_null

    if ast.should_return_null:
        for i, e in zip(ast.try_body.element_nodes, expected.try_body.element_nodes):
            assert i.value == e.value
    else:
        assert ast.try_body.value == expected.try_body.value

    if ast.except_body:
        for i, e in zip(ast.except_body.element_nodes, expected.except_body.element_nodes):
            assert i.value == e.value

    if ast.except_name:
        assert ast.except_name.value == expected.except_name.value

    if ast.except_as:
        assert ast.except_as.value == expected.except_as.value


@ pytest.mark.parametrize("test_input,expected", [
    ("pro i = 1 ad 1: 1", ForNode("i", NumberNode(1, basepos, basepos), NumberNode(1, basepos, basepos), None, NumberNode(1, basepos, basepos), False, basepos, basepos)),
    ("pro i = 1 ad 1:;    1", ForNode("i", NumberNode(1, basepos, basepos), NumberNode(
        1, basepos, basepos), None, body, True, basepos, basepos)),
    ("pro i = 1 ad 1 gradus 1:;    1", ForNode("i", NumberNode(1, basepos, basepos), NumberNode(
        1, basepos, basepos), NumberNode(1, basepos, basepos), body, True, basepos, basepos))
])
def test_parser_for_node(test_input, expected):
    ast = parser_test_base(test_input)

    assert ast.var_name == expected.var_name
    assert ast.start_value_node.value == expected.start_value_node.value
    assert ast.end_value_node.value == expected.end_value_node.value
    assert ast.should_return_null == expected.should_return_null

    if ast.should_return_null:
        for i, e in zip(ast.body_node.element_nodes, expected.body_node.element_nodes):
            assert i.value == e.value
    else:
        assert ast.body_node.value == expected.body_node.value

    if ast.step_value_node:
        assert ast.step_value_node.value == expected.step_value_node.value


@ pytest.mark.parametrize("test_input,expected", [
    ("dum 1: 1", WhileNode(NumberNode(1, basepos, basepos), NumberNode(1, basepos, basepos), False, basepos, basepos)),
    ("dum 1:;    1", WhileNode(NumberNode(1, basepos, basepos), body, True, basepos, basepos)),
])
def test_parser_while_node(test_input, expected):
    ast = parser_test_base(test_input)

    assert ast.condition_node.value == expected.condition_node.value
    assert ast.should_return_null == expected.should_return_null
    if ast.should_return_null:
        for i, e in zip(ast.body_node.element_nodes, expected.body_node.element_nodes):
            assert i.value == e.value
    else:
        assert ast.body_node.value == expected.body_node.value


@pytest.mark.parametrize("test_input,expected", [
    ("opus () -> 1", FuncDefNode(None, [], NumberNode(1, basepos, basepos), True, basepos, basepos)),
    ("opus (x) -> 1", FuncDefNode(None, ["x"], NumberNode(1, basepos, basepos), True, basepos, basepos)),
    ("opus (x,x) -> 1", FuncDefNode(None, ["x", "x"], NumberNode(1, basepos, basepos), True, basepos, basepos)),
    ("opus x(x) -> 1", FuncDefNode("x", ["x"], NumberNode(1, basepos, basepos), True, basepos, basepos)),
    ("opus x(x):;    1", FuncDefNode("x", ["x"], body, False, basepos, basepos))
])
def test_parser_func_def(test_input, expected):
    ast = parser_test_base(test_input)

    assert ast.func_name == expected.func_name
    for idx, e in enumerate(expected.args):
        assert ast.args[idx] == e
    assert ast.should_auto_return == expected.should_auto_return
    if expected.should_auto_return:
        assert ast.body_node.value == expected.body_node.value
    else:
        for i, e in zip(ast.body_node.element_nodes, expected.body_node.element_nodes):
            assert i.value == e.value


@pytest.mark.parametrize("test_input,expected", [
    ("1()", CallNode(NumberNode(1, basepos, basepos), [], basepos, basepos)),
    ("1(1)", CallNode(NumberNode(1, basepos, basepos), [NumberNode(1, basepos, basepos)], basepos, basepos))
])
def test_parser_call(test_input, expected):
    ast = parser_test_base(test_input)

    assert ast.node_to_call.value == expected.node_to_call.value
    if ast.arg_nodes:
        for i, e in zip(ast.arg_nodes, expected.arg_nodes):
            assert i.value == e.value


@ pytest.mark.parametrize("test_input,expected", [
    ("redi 1", ReturnNode(NumberNode(1, basepos, basepos), basepos, basepos)),
    ("continua", ContinueNode(basepos, basepos)),
    ("confringe", BreakNode(basepos, basepos)),
])
def test_parser_misc_nodes(test_input, expected):
    ast = parser_test_base(test_input)
    if isinstance(expected, ReturnNode):
        assert ast.node_to_return.value == expected.node_to_return.value
    if isinstance(expected, ContinueNode):
        assert isinstance(ast, ContinueNode)
    if isinstance(expected, BreakNode):
        assert isinstance(ast, BreakNode)
