#######################################
# IMPORTS
#######################################

from helper.errors import *
from lexer.Lexer import *
from parser.parser import Parser
from interpreter.interpreter import *

#######################################
# RUN
#######################################


global_symbol_table = SymbolTable()
global_symbol_table.set("nil", Number.null)
global_symbol_table.set("falsus", Number.false)
global_symbol_table.set("verus", Number.true)
global_symbol_table.set("pi", Number.math_PI)
global_symbol_table.set("scribe", BuiltInFunction.print)
global_symbol_table.set("initus", BuiltInFunction.input)
global_symbol_table.set("purgo", BuiltInFunction.clear)
global_symbol_table.set("est_numerus", BuiltInFunction.is_number)
global_symbol_table.set("est_filum", BuiltInFunction.is_string)
global_symbol_table.set("est_album", BuiltInFunction.is_list)
global_symbol_table.set("est_opus", BuiltInFunction.is_function)
global_symbol_table.set("adde", BuiltInFunction.append)
global_symbol_table.set("remove", BuiltInFunction.pop)
global_symbol_table.set("extende", BuiltInFunction.extend)
global_symbol_table.set("longitudo", BuiltInFunction.len)
global_symbol_table.set("curre", BuiltInFunction.run)


def run(fn, text):
    # Generate tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    # Generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    # Run program
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error
