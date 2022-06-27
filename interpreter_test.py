import pytest
from lexer.Lexer import *
from parser.parser import *
from interpreter.interpreter import *
from helper.tokens import *
from root.root import *


def interpreter_test_base(test_input):
    lexer = Lexer("<stdin>", test_input)
    tokens, _ = lexer.make_tokens()

    parser = Parser(tokens)
    ast = parser.parse()

    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    assert result.error == None
    return result.value
