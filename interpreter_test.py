#######################################
# IMPORTS
#######################################

import pytest
from lexer import Lexer
from parser import Parser
from interpreter import *

#######################################
# TESTS
#######################################


def interpreter_test_base(test_input):
    lexer = Lexer("<stdin>", test_input)
    tokens, _ = lexer.make_tokens()

    parser = Parser(tokens)
    ast = parser.parse()

    interpreter = Interpreter()
    context = Context('<program>')
    symbol_table = SymbolTable()
    context.symbol_table = symbol_table
    result = interpreter.visit(ast.node, context)

    assert result.error == None
    return result.value
