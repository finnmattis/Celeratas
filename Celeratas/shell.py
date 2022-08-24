#######################################
# IMPORTS
#######################################

# Readline will make the up and down arrows cycle through history
import readline
import sys
from datetime import datetime

import inquirer

import Celeratas.interpreter.constants as constants
from Celeratas.helper.errors import InteractivePrompt

from .interpreter.Context import Context
from .interpreter.Interpreter import Interpreter
from .interpreter.SymbolTable import SymbolTable
from .interpreter.values import List
from .lexer.Lexer import Lexer
from .parser.Parser import Parser

#######################################
# GLOBAL SYMBOL TABLE
#######################################

global_symbol_table = SymbolTable()
global_symbol_table.set("nil", constants.Number.null)
global_symbol_table.set("pi", constants.Number.math_PI)
global_symbol_table.set("scribe", constants.BuiltInFunction.print)
global_symbol_table.set("initus", constants.BuiltInFunction.input)
global_symbol_table.set("purgo", constants.BuiltInFunction.clear)
global_symbol_table.set("est_numerus", constants.BuiltInFunction.is_number)
global_symbol_table.set("est_filum", constants.BuiltInFunction.is_string)
global_symbol_table.set("est_album", constants.BuiltInFunction.is_list)
global_symbol_table.set("est_opus", constants.BuiltInFunction.is_function)
global_symbol_table.set("adde", constants.BuiltInFunction.append)
global_symbol_table.set("remove", constants.BuiltInFunction.pop)
global_symbol_table.set("extende", constants.BuiltInFunction.extend)
global_symbol_table.set("longitudo", constants.BuiltInFunction.len)
global_symbol_table.set("finde", constants.BuiltInFunction.split)
global_symbol_table.set("curre", constants.BuiltInFunction.run)
#######################################
# RUN SCRIPT FUNCTION
#######################################

# Function Out of class because curre() needs to access it


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
    interpreter = Interpreter(recursion_depth=0)
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
            num_prompt = [
                inquirer.List('num',
                              message="What do you need help with?",
                              choices=['Keywords', 'Syntax', 'Built-In Functions', 'Leave'],
                              carousel=True,
                              ),
            ]
            # try block to quit help menu on keyboard interupt but not overall program - it catches type error bc of inquirer jank
            try:
                num = inquirer.prompt(num_prompt)["num"]
            except TypeError:
                return None

            if num == "Keywords":
                print('\nVerus -> True\nFalsus -> False\net -> and\naut -> or\nnon -> not\nsi -> if')
                print('alioquinsi -> elif\nalioquin -> else\ntempta -> try\npraeter -> except\ntam -> as\npro -> for')
                print('ad -> to\ngradus -> step\ndum -> while\nopus -> task\nredi -> return')
                print('continua -> continue\nconfringe -> break\ntransiet -> pass\nattolle -> raise\n')
            elif num == "Syntax":
                with open("Celeratas/helper/grammar.txt", "r") as grammar:
                    print(f"{grammar.read()}\n")
            elif num == "Built-In Functions":
                print('\nscribe(value_to_print) -> print\ninitus(message_to_print) -> input\npurgo() -> clear\nest_numerus(value_to_check) -> is_number')
                print('est_filum(value_to_check) -> is_string\nest_album(value_to_check) -> is_list\nest_opus(value_to_check) -> is_function')
                print('adde(value_to_add) -> append\nremove(value_to_remove) -> pop\nextende(list_to_extend) -> extend\nlongitudo(value_to_check) -> length')
                print('finde(string_to_split, seperator) -> split\ncurre(file_to_run) -> run\n')
            else:
                break

            continue_prompt = [
                inquirer.List('continue',
                              message="Do you need anything else?",
                              choices=['I need more help!', 'I\'m all good!'],
                              carousel=True,
                              ),
            ]

            try:
                continue_ = inquirer.prompt(continue_prompt)["continue"]
            except TypeError:
                return None

            if continue_ == "I need more help!":
                continue
            else:
                break

    #######################################
    # GET RESULT FUNCTION
    #######################################

    def get_result(self, fn, script, interactive):
        result, error = run_script(fn, script)
        result = [x for x in result.elements if x is not None] if result else None

        if error:
            if isinstance(error, InteractivePrompt):
                return error.symbol
            elif error:
                print(error.as_string())

        elif result and interactive:
            if len(result) == 1:
                print(repr(result[0]))
            else:
                print(repr(result))

        return None

    #######################################
    # RUN FILE FROM CLI ARGS OR TAKE INPUT
    #######################################

    def start(self):
        global_symbol_table.set("__args__", List(sys.argv[2:]) if len(sys.argv) > 2 else List([]))
        try:
            # Read file from CLI args
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
                # Interactive Mode
                time = self.get_time()
                print(
                    f"Celeratas versio unum.tres (defalta, {time})\nScribe 'auxilium' auxilio")
                more_statements = False
                statements_txt = ""
                prompt_symbol = ""

                while True:
                    text = input(f"{prompt_symbol * 3} " if more_statements else ">>> ")

                    if text == "auxilium" and not more_statements:
                        self.help_menu()
                        continue

                    # Blank input should be ignored while not being prompted '...' otherwise it should end the statement
                    if text.strip() == "":
                        if more_statements:
                            self.get_result(
                                "<stdin>", statements_txt, interactive=True)
                            more_statements = False
                            continue
                        else:
                            continue

                    if more_statements:
                        # Add another line and tab to the new line and add it to the statement
                        statements_txt += f"\n{text.rjust(len(text) + 4)}"
                    else:
                        prompt_symbol = self.get_result(
                            "<stdin>", text, interactive=True)
                        # Error is true when program throws an interactive error
                        if prompt_symbol:
                            more_statements = True
                            statements_txt = text

        except KeyboardInterrupt:
            print("\r", end="")
            print("Keyboard Interrupt")

# For entry point:


def start():
    Shell()
