#######################################
# IMPORTS
#######################################

import Celeratas.helper.tokens as toks
import pytest
from Celeratas.lexer.Lexer import Lexer
from Celeratas.lexer.Position import Position
from Celeratas.lexer.Token import Token
from Celeratas.parser.nodes import (BinOpNode, BreakNode, CallNode,
                                    ContinueNode, ForNode, FuncDefNode, IfNode,
                                    ListNode, NumberNode, NumeralNode,
                                    ReturnNode, StringNode, TryNode,
                                    UnaryOpNode, VarAccessNode, VarAssignNode,
                                    WhileNode)
from Celeratas.parser.Parser import Parser

#######################################
# TESTS
#######################################
basepos = Position(0, 0, 0, "<stdin>", "1")
# Use basepos because error location does not matter

# NOTE Didn't use zip bc it skips over loops if the result does not have the same number of elements as expected - Therefore, I used enumerate instead


def parser_test_base(test_input, should_fail=False):
    lexer = Lexer("<std_in>", test_input)
    tokens, error = lexer.make_tokens()

    assert not error

    parser = Parser(tokens)
    ast = parser.parse()

    if should_fail:
        assert ast.error
        return None
    else:
        assert not ast.error
        return ast.node.element_nodes[0]


@pytest.mark.parametrize("test_input,expected", [
    ("1", NumberNode(1, basepos, basepos)),
    ("IV", NumeralNode(4, basepos, basepos)),
])
def test_parser_numbers(test_input, expected):
    res = parser_test_base(test_input)
    assert res.value == expected.value


@pytest.mark.parametrize("test_input,expected", [
    ("\"x\"", StringNode(["x"], basepos, basepos)),
    ("f\"{1}\"", StringNode(
        [NumberNode(1, basepos, basepos)], basepos, basepos))
])
def test_parser_strings(test_input, expected):
    res = parser_test_base(test_input)

    for i, e in enumerate(expected.str_components):
        i = res.str_components[i]

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
    res = parser_test_base(test_input)
    assert res.op_tok.type == expected.op_tok.type
    assert res.node.value == expected.node.value


@pytest.mark.parametrize("test_input,expected", [
    ("1+1", BinOpNode(NumberNode(1, basepos, basepos),
     Token(toks.TT_PLUS, basepos), NumberNode(1, basepos, basepos), basepos, basepos))
])
def test_parser_bin_op(test_input, expected):
    res = parser_test_base(test_input)

    assert res.op_tok.type == expected.op_tok.type
    assert res.left_node.value == expected.left_node.value
    assert res.right_node.value == expected.right_node.value


@pytest.mark.parametrize("test_input,expected,should_fail", [
    ("[1, 2, 3]", ListNode([NumberNode(1, basepos, basepos), NumberNode(
        2, basepos, basepos), NumberNode(3, basepos, basepos)], basepos, basepos), False),
    ("[x = 10]", [], True),
])
def test_parser_list(test_input, expected, should_fail):
    res = parser_test_base(test_input, should_fail)

    if not should_fail:
        for i, e in enumerate(expected.element_nodes):
            i = res.element_nodes[i]
            assert i.value == e.value


@pytest.mark.parametrize("test_input,expected", [
    ("x", VarAccessNode("x", [], [], basepos, basepos)),
    ("x[0]", VarAccessNode("x", [NumberNode(0, basepos, basepos)], [], basepos, basepos)),
    ("x[0][0]", VarAccessNode("x", [NumberNode(0, basepos, basepos), NumberNode(0, basepos, basepos)], [], basepos, basepos)),
    ("x.attr", VarAccessNode("x", [], ["attr"], basepos, basepos)),
    ("x[0].attr", VarAccessNode("x", [NumberNode(0, basepos, basepos)], ["attr"], basepos, basepos)),
    ("x[0].attr.attr", VarAccessNode("x", [NumberNode(0, basepos, basepos)], ["attr", "attr"], basepos, basepos)),
])
def test_parser_var_access(test_input, expected):
    res = parser_test_base(test_input)
    assert res.var_name_to_get == expected.var_name_to_get
    for idx, e in enumerate(expected.attrs_to_get):
        i = res.attrs_to_get[idx]
        assert i == e

    for i, e in enumerate(expected.idxes_to_get):
        i = res.idxes_to_get[i]
        assert i.value == e.value


@pytest.mark.parametrize("test_input,expected", [
    ("x = 1", VarAssignNode([["x", []]], [NumberNode(1, basepos, basepos)], Token(toks.TT_EQ, basepos), basepos, basepos)),
    ("x += 1", VarAssignNode([["x", []]], [NumberNode(1, basepos, basepos)], Token(toks.TT_PLUS_EQ, basepos), basepos, basepos)),
    ("x[0] = 1", VarAssignNode([["x", [NumberNode(0, basepos, basepos)]]], [NumberNode(1, basepos, basepos)], Token(toks.TT_EQ, basepos), basepos, basepos)),
    ("a, b = 1, 2", VarAssignNode([["a", []], ["b", []]], [NumberNode(1, basepos, basepos),
     NumberNode(2, basepos, basepos)], Token(toks.TT_EQ, basepos), basepos, basepos)),

])
def test_parser_var_assign(test_input, expected):
    res = parser_test_base(test_input)

    assert res.vars_to_set[0][0] == expected.vars_to_set[0][0]

    for i, e in enumerate(expected.vars_to_set[0][1]):
        i = res.vars_to_set[0][1][i]
        assert i.value == e.value
    for i, e in enumerate(expected.values_to_set):
        i = res.values_to_set[i]
        assert i.value == e.value
    assert res.assign_type.type == expected.assign_type.type


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
def test_parser_if(test_input, expected):
    res = parser_test_base(test_input)

    for i, e in enumerate(res.cases):
        i = res.cases[i]
        assert i[0].value == e[0].value
        assert i[2] == e[2]

        if e[2]:
            for i1, e2 in enumerate(e[1].element_nodes):
                i1 = i[1].element_nodes[i1]
                assert i1.value == e2.value
        else:
            assert i[1].value == e[1].value

    if res.else_case:
        assert res.else_case[1] == expected.else_case[1]

        for i, e in zip(res.else_case[0].element_nodes, expected.else_case[0].element_nodes):
            assert i.value == e.value


body = ListNode([NumberNode(1, basepos, basepos)], basepos, basepos)


@ pytest.mark.parametrize("test_input,expected", [
    ("tempta:    1", TryNode(NumberNode(1, basepos, basepos), None, None, None, False, basepos, basepos)),
    ("tempta:;    1", TryNode(body, None, None, None, True, basepos, basepos)),
    ("tempta:;    1;praeter:;    1", TryNode(body, body, None, None, True, basepos, basepos)),
    ("tempta:;    1;praeter Exception:;    1", TryNode(body, body, Token(toks.TT_IDENTIFIER, "Exception"), None, True, basepos, basepos)),
    ("tempta:;    1;praeter Exception tam e:;    1;", TryNode(body, body, Token(toks.TT_IDENTIFIER, "Exception"), Token(toks.TT_IDENTIFIER, "e"), True, basepos, basepos)),
])
def test_parser_try(test_input, expected):
    res = parser_test_base(test_input)

    assert res.should_return_null == expected.should_return_null

    if res.should_return_null:
        for i, e in enumerate(expected.try_body.element_nodes):
            i = res.try_body.element_nodes[i]
            assert i.value == e.value
    else:
        assert res.try_body.value == expected.try_body.value

    if res.except_body:
        for i, e in enumerate(expected.except_body.element_nodes):
            i = res.except_body.element_nodes[i]
            assert i.value == e.value

    if res.except_name:
        assert res.except_name.value == expected.except_name.value
    if res.except_as:
        assert res.except_as.value == expected.except_as.value


@ pytest.mark.parametrize("test_input,expected", [
    ("pro i = 1 ad 1: 1", ForNode("i", NumberNode(1, basepos, basepos), NumberNode(1, basepos, basepos), None, NumberNode(1, basepos, basepos), False, basepos, basepos)),
    ("pro i = 1 ad 1:;    1", ForNode("i", NumberNode(1, basepos, basepos), NumberNode(
        1, basepos, basepos), None, body, True, basepos, basepos)),
    ("pro i = 1 ad 1 gradus 1:;    1", ForNode("i", NumberNode(1, basepos, basepos), NumberNode(
        1, basepos, basepos), NumberNode(1, basepos, basepos), body, True, basepos, basepos))
])
def test_parser_for(test_input, expected):
    res = parser_test_base(test_input)

    assert res.var_name == expected.var_name
    assert res.start_value_node.value == expected.start_value_node.value
    assert res.end_value_node.value == expected.end_value_node.value
    assert res.should_return_null == expected.should_return_null

    if res.should_return_null:
        for i, e in enumerate(expected.body_node.element_nodes):
            i = res.body_node.element_nodes[i]
            assert i.value == e.value
    else:
        assert res.body_node.value == expected.body_node.value

    if res.step_value_node:
        assert res.step_value_node.value == expected.step_value_node.value


@ pytest.mark.parametrize("test_input,expected", [
    ("dum 1: 1", WhileNode(NumberNode(1, basepos, basepos), NumberNode(1, basepos, basepos), False, basepos, basepos)),
    ("dum 1:;    1", WhileNode(NumberNode(1, basepos, basepos), body, True, basepos, basepos)),
])
def test_parser_while(test_input, expected):
    res = parser_test_base(test_input)

    assert res.condition_node.value == expected.condition_node.value
    assert res.should_return_null == expected.should_return_null

    if res.should_return_null:
        for i, e in enumerate(expected.body_node.element_nodes):
            i = res.body_node.element_nodes[i]
            assert i.value == e.value
    else:
        assert res.body_node.value == expected.body_node.value


@pytest.mark.parametrize("test_input,expected,should_fail", [
    ("() => 1", FuncDefNode(None, [], NumberNode(1, basepos, basepos), True, basepos, basepos), False),
    ("(x) => 1", FuncDefNode(None, [("x", None)], NumberNode(1, basepos, basepos), True, basepos, basepos), False),
    ("(x=1) => 1", FuncDefNode(None, [("x", NumberNode(1, basepos, basepos))], NumberNode(1, basepos, basepos), True, basepos, basepos), False),
    ("(x1,x2) => 1", FuncDefNode(None, [("x1", None), ("x2", None)], NumberNode(1, basepos, basepos), True, basepos, basepos), False),
    ("(x,x) => 1", [], True),
    ("(x1,x2=1) => 1", FuncDefNode(None, [("x1", None), ("x2", NumberNode(1, basepos, basepos))], NumberNode(1, basepos, basepos), True, basepos, basepos), False),
    ("(x1=1,x2) => 1", [], True),
    ("(x) => 1", FuncDefNode(None, [("x", None)], NumberNode(1, basepos, basepos), True, basepos, basepos), False),
    ("opus x(x):;    1", FuncDefNode("x", [("x", None)], body, False, basepos, basepos), False)
])
def test_parser_func_def(test_input, expected, should_fail):
    res = parser_test_base(test_input, should_fail)

    if not should_fail:
        assert res.func_name == expected.func_name
        assert res.should_auto_return == expected.should_auto_return

        for i, e in enumerate(expected.args):
            i = res.args[i]
            assert i[0] == e[0]
            if e[1]:
                assert i[1].value == e[1].value

        if expected.should_auto_return:
            assert res.body_node.value == expected.body_node.value
        else:
            for i, e in zip(res.body_node.element_nodes, expected.body_node.element_nodes):
                assert i.value == e.value


@pytest.mark.parametrize("test_input,expected,should_fail", [
    ("1()", CallNode(NumberNode(1, basepos, basepos), {}, basepos, basepos), False),
    ("1(1)", CallNode(NumberNode(1, basepos, basepos), {0: NumberNode(1, basepos, basepos)}, basepos, basepos), False),
    ("1(1, 1)", CallNode(NumberNode(1, basepos, basepos), {0: NumberNode(1, basepos, basepos), 1: NumberNode(1, basepos, basepos)}, basepos, basepos), False),
    ("1(x=1)", CallNode(NumberNode(1, basepos, basepos), {"x": NumberNode(1, basepos, basepos)}, basepos, basepos), False),
    ("1(x, x=1)", CallNode(NumberNode(1, basepos, basepos), {"x": NumberNode(1, basepos, basepos)}, basepos, basepos), False),
    ("1(x=1, x)", [], True)
])
def test_parser_call(test_input, expected, should_fail):
    res = parser_test_base(test_input, should_fail)

    if not should_fail:
        assert res.node_to_call.value == expected.node_to_call.value
        for key, value in expected.arg_nodes.items():
            assert value.value == res.arg_nodes[key].value


@ pytest.mark.parametrize("test_input,expected,should_fail", [
    ("opus x():;    redi 1", FuncDefNode("x", [], ListNode([ReturnNode(NumberNode(1, basepos, basepos), basepos, basepos)], basepos, basepos), False, basepos, basepos), False),
    ("redi 1", ReturnNode(NumberNode(1, basepos, basepos), basepos, basepos), True),
    ("dum 1:;    continua", WhileNode(NumberNode(1, basepos, basepos), ListNode([ContinueNode(basepos, basepos)], basepos, basepos), True, basepos, basepos), False),
    ("continua", ContinueNode(basepos, basepos), True),
    ("dum 1:;    confringe", WhileNode(NumberNode(1, basepos, basepos), ListNode([BreakNode(basepos, basepos)], basepos, basepos), True, basepos, basepos), False),
    ("confringe", BreakNode(basepos, basepos), True),
])
def test_parser_misc(test_input, expected, should_fail):
    res = parser_test_base(test_input, should_fail)
    if not should_fail:
        if isinstance(expected, FuncDefNode):
            for i, e in enumerate(expected.body_node.element_nodes):
                i = res.body_node.element_nodes[i]
                assert i.node_to_return.value == e.node_to_return.value

        if isinstance(expected, ReturnNode):
            assert isinstance(res, ReturnNode)
            assert res.node_to_return.value == expected.node_to_return.value
        if isinstance(expected, ContinueNode):
            assert isinstance(res, ContinueNode)
        if isinstance(expected, BreakNode):
            assert isinstance(res, BreakNode)
