#######################################
# IMPORTS
#######################################

import pytest
from Celeratas.interpreter.Context import Context
from Celeratas.interpreter.Interpreter import Interpreter
from Celeratas.interpreter.SymbolTable import SymbolTable
from Celeratas.interpreter.values import (Bool, Dict, List, Number, Numeral,
                                          String)
from Celeratas.lexer.Lexer import Lexer
from Celeratas.parser.Parser import Parser

#######################################
# TESTS
#######################################


def interpreter_test_base(test_input, should_fail=False):
    lexer = Lexer("<stdin>", test_input)
    tokens, _ = lexer.make_tokens()

    parser = Parser(tokens)
    ast = parser.parse()

    interpreter = Interpreter(0)
    context = Context('<program>')
    symbol_table = SymbolTable()
    context.symbol_table = symbol_table
    result = interpreter.visit(ast.node, context)

    if should_fail:
        assert ast.error
        return None
    else:
        assert result.error is None
        return result.value.elements


@pytest.mark.parametrize("test_input, expected", [
    ("1", Number(1)),
    ("I", Numeral(1)),
    ("\"x\"", String("x")),
    ("f\"{1}\"", String("1")),
    ("Verus", Bool(True)),
    ("Falsus", Bool(False)),
])
def test_interpreter_datatypes(test_input, expected):
    res = interpreter_test_base(test_input)[0]
    assert res.value == expected.value


@pytest.mark.parametrize("test_input, expected", [
    ("[1, 2]", List([Number(1), Number(2)])),
])
def test_interpreter_lists(test_input, expected):
    res = interpreter_test_base(test_input)[0]
    for i, e in enumerate(expected.elements):
        i = res.elements[i]
        assert i.value == e.value


@pytest.mark.parametrize("test_input, expected", [
    ("{1:1}", Dict({Number(1): Number(1)})),
])
def test_interpreter_dicts(test_input, expected):
    res = interpreter_test_base(test_input)[0]
    for (e_key, e_value) in zip(expected.key_pairs, res.key_pairs):
        assert e_key == e_key
        assert e_value == e_value


@pytest.mark.parametrize("test_input, expected", [
    ("a = 1;a", Number(1)),
    ("a = [1];a", List([Number(1)])),
    ("a = [1];a[0]", Number(1)),
    ("a = [[1]];a[0][0", Number(1)),
    ("a = {1:1};a[1]", Number(1)),
])
def test_interpreter_var_assign(test_input, expected):
    res = interpreter_test_base(test_input)[1]
    if isinstance(expected, List):
        assert isinstance(res, List)
        for i, e in enumerate(expected.elements):
            i = res.elements[i]
            assert i.value == e.value
    else:
        assert res.value == expected.value


test_interpreter_var_assign("a = 5;a", Number(5))
