from tokenize import Number
import pytest
from main.lexer import *
from main.parser import *
from helper.tokens import *

basepos = Position(0, 0, 0, "<stdin>", "1")

# Use basepos because error location does not matter


@pytest.mark.parametrize("test_input,expected", [
    # Test Numbers, Numerals, and Strings:
    ("1", [NumberNode(Token(TT_INT, 1, basepos))]),
    ("IV", [NumeralNode(Token(TT_NUMERAL, 4, basepos))]),
    ("\"x\"", [StringNode(Token(TT_STRING, "x", basepos))]),
    # Test Un/Bin Op Node:
    ("-1", [UnaryOpNode(Token(TT_MINUS, pos_start=basepos),
     NumberNode(Token(TT_INT, 1, basepos)))]),
    ("1+1", [BinOpNode(NumberNode(Token(TT_INT, 1, basepos)),
     Token(TT_PLUS, pos_start=basepos), NumberNode(Token(TT_INT, 1, basepos)))]),
    # Test lists and Var Access
    ("[1, 2, 3]", [ListNode(element_nodes=[NumberNode(Token(TT_INT, 1, basepos)), NumberNode(
        Token(TT_INT, 2, basepos)), NumberNode(Token(TT_INT, 3, basepos))], pos_start=basepos, pos_end=basepos)]),
    ("x", [VarAccessNode(Token(TT_IDENTIFIER, "x", basepos), [])]),
    ("x[0]", [VarAccessNode(Token(TT_IDENTIFIER, "x", basepos),
     [NumberNode(Token(TT_INT, 0, basepos))])]),
    ("x[a]", [VarAccessNode(Token(TT_IDENTIFIER, "x", basepos),
     [VarAccessNode(Token(TT_IDENTIFIER, "a", basepos), [])])]),
    # Test Var Assign
    ("x = 1", [VarAssignNode(Token(TT_IDENTIFIER, "x", basepos),
     NumberNode(Token(TT_INT, 1, basepos)), [], False)])
])
def test_parser(test_input, expected):
    lexer = Lexer("<std_in>", test_input)
    tokens, _ = lexer.make_tokens()

    parser = Parser(tokens)
    ast = parser.parse()

    assert ast.error == None

    for (output, expected_out) in zip(ast.node.element_nodes, expected):
        if type(output) == ListNode:
            for (out_el, exp_out_el) in zip(output.element_nodes, expected_out.element_nodes):
                assert out_el.tok.value == exp_out_el.tok.value
        elif type(output) == UnaryOpNode:
            assert output.op_tok.type == expected_out.op_tok.type
            assert output.node.tok.value == expected_out.node.tok.value
        elif type(output) == BinOpNode:
            assert output.left_node.tok.value == expected_out.left_node.tok.value
            assert output.op_tok.type == expected_out.op_tok.type
            assert output.right_node.tok.value == expected_out.left_node.tok.value
        elif type(output) == VarAccessNode:
            assert output.var_name_tok.value == expected_out.var_name_tok.value
            for (out_idx_to_get, exp_out_idx_to_get) in zip(output.idxes_to_get, expected_out.idxes_to_get):
                if type(out_idx_to_get) == NumberNode:
                    assert out_idx_to_get.tok.value == exp_out_idx_to_get.tok.value
                if type(out_idx_to_get) == VarAccessNode:
                    assert out_idx_to_get.var_name_tok.value == exp_out_idx_to_get.var_name_tok.value
        elif type(output) == VarAssignNode:
            assert output.var_name_tok.value == expected_out.var_name_tok.value
            assert output.value_node.tok.value == expected_out.value_node.tok.value
            assert output.idxes_to_change == expected_out.idxes_to_change
            assert output.global_var == output.global_var
        else:
            assert output.tok.value == expected_out.tok.value
