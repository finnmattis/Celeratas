#######################################
# IMPORTS
#######################################

from Celeratas.interpreter.Context import Context
from Celeratas.interpreter.Interpreter import Interpreter
from Celeratas.interpreter.SymbolTable import SymbolTable
from Celeratas.lexer.Lexer import Lexer
from Celeratas.parser.Parser import Parser

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

    assert result.error is None
    return result.value
