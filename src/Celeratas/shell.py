#!/usr/bin/python3

#######################################
# IMPORTS
#######################################

import sys
from datetime import datetime

from .lexer.Lexer import Lexer
from .parser.Parser import Parser
from .interpreter.Interpreter import Interpreter
from .interpreter.SymbolTable import SymbolTable
from .interpreter.Context import Context
from .interpreter.values import Number, BuiltInFunction

#######################################
# GLOBAL SYMBOL TABLE
#######################################

global_symbol_table = SymbolTable()
global_symbol_table.set("nil", Number.null)
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
#######################################
# RUN SCRIPT FUNCTION
#######################################

# Function Out oo class because curre() needs to access it


def run_script(fn, text):
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


class Shell:
    def __init__(self):
        self.start()

    #######################################
    # DATE
    #######################################

    def get_time(self):
        time = datetime.now().strftime("%b %d %y, %H:%M:%S")
        time = time.replace("Jan", "Unus Martius").replace(
            "Feb", "Duo Martius")
        time = time.replace("Mar", "Martius").replace("Apr", "Aprilis")
        time = time.replace("May", "Maius").replace("Jun", "Junius")
        time = time.replace("Jul", "Quintilis").replace("Aug", "Sextilis")
        return time
        # Don't need to replace Sep, Oct, Nov, or Dec bc they are the same in latin

    #######################################
    # HELP FUNCTION
    #######################################

    def help_menu(self):
        while True:
            print(
                "\nWhat do you need help with?\n\n1: Keywords\n2: Syntax\n3: Built-In Functions\n4: Leave\n")
            while True:
                help_num = input()
                if help_num in ["1", "2", "3", "4"]:
                    break
                else:
                    print("\nPlease only type 1, 2, 3, or 4\n")

            if help_num == "1":
                print('\nVerus -> True\nFalsus -> False\net -> and\naut -> or\nnon -> not\nsi -> if\nalioquinsi -> elif\nalioquin -> else\ntempta -> try\npraeter -> except\tam -> as\nnpro -> for')
                print('ad -> to\ngradus -> step\ndum -> while\nopus -> task\nfinis -> end\nredi -> return\ncontinua -> continue\nconfringe -> break')
            elif help_num == "2":
                with open("src/helper/grammar.txt", "r") as grammar:
                    print(f"\n{grammar.read()}")
            elif help_num == "3":
                print('\nscribe(value_to_print) -> print\ninitus() -> input\npurgo() -> clear\nest_numerus(value_to_check) -> is_number\nest_filum(value_to_check) -> is_string\nest_album(value_to_check) -> is_list')
                print('est_opus(value_to_check) -> is_function\nadde(value_to_add) -> append\nremove(value_to_remove) -> pop\nextende(list_to_extend) -> extend\nlongitudo(value_to_check) -> length\ncurre(file_to_run) -> run')
            else:
                break

    #######################################
    # GET RESULT FUNCTION
    #######################################

    def get_result(self, fn, script, interactive):
        result, error = run_script(fn, script)

        if hasattr(error, "interactive") and error.interactive == True:
            return True
        elif error:
            print(error.as_string())
        elif result:
            result.elements = [x for x in result.elements if repr(x) != "None"]
            if len(result.elements) == 0:
                pass
            elif len(result.elements) == 1:
                print(repr(result.elements[0]))
            else:
                print(repr(result))
        return False

    #######################################
    # RUN FILE FROM CLI ARGS OR TAKE INPUT
    #######################################

    def start(self):
        try:
            if len(sys.argv) > 1:
                try:
                    fn = sys.argv[1]
                    with open(fn, "r") as f:
                        script = f.read()
                    self.get_result(fn, script, interactive=False)
                except FileNotFoundError:
                    print(f"Can't open file {fn}: No such file")
                except UnicodeDecodeError:
                    print(f"Can't open file {fn}: Invalid file format")
            else:
                time = self.get_time()
                print(
                    f"Celeritas versio unum (defalta, {time})\nScribe 'auxilium' auxilio")
                more_statements = False
                statements_txt = ""

                while True:
                    text = input("... " if more_statements else ">>> ")

                    if text == "auxilium" and not more_statements:
                        self.help_menu()
                        continue

                    if text.strip() == "":
                        if more_statements:
                            self.get_result(
                                "<stdin>", statements_txt, interactive=False)
                            more_statements = False
                            continue
                        else:
                            continue

                    if more_statements:
                        statements_txt += f"\n{text.rjust(len(text) + 4)}"
                    else:
                        error = self.get_result(
                            "<stdin>", text, interactive=False)
                        # Error is true when program throws an interactive error
                        if error:
                            more_statements = True
                            statements_txt = text

        except KeyboardInterrupt:
            print("\r", end="")
            print("Keyboard Interrupt")


def main():
    Shell = Shell()
