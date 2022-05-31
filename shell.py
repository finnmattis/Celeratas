
# TODO Add Zeros to Numerals
# TODO Add more list functionality

# TODO Future: Use indents instead of finis{end}
# TODO Future: Create STD LIB
# TODO Future: Create vscode extension
# TODO FUture: Create website


#######################################
# IMPORTS
#######################################

import sys
from datetime import datetime

import root

#######################################
# Date
#######################################


def get_time():
    time = datetime.now().strftime("%b %d %y, %H:%M:%S")
    time = time.replace("Jan", "Unus Martius").replace("Feb", "Duo Martius")
    time = time.replace("Mar", "Martius").replace("Apr", "Aprilis")
    time = time.replace("May", "Maius").replace("Jun", "Junius")
    time = time.replace("Jul", "Quintilis").replace("Aug", "Sextilis")
    return time
    # Don't need to replace Sep, Oct, Nov, or Dec bc they are the same in latin

#######################################
# Help Function
#######################################


def help_menu():
    print("\nWhat do you need help with?\n\n1: Keywords\n2: Syntax\n3: Built-In Functions\n")
    while True:
        help_num = input()
        if help_num in ["1", "2", "3"]:
            break
        else:
            print("\nPlease only type 1, 2, or 3\n")
    if help_num == "1":
        print('\nsino -> var\net -> and\naut -> or\nnon -> not\nsi -> if\nalioquinsi -> elif\nalioquin -> else\npro -> for')
        print('ad -> to\ngradus -> step\ndum -> while\nopus -> task\nfinis -> end\nredi -> return\ncontinua -> continue\nconfringe -> break')
    elif help_num == "2":
        print(
            """{} = English Meaning of KEYWORD

statements: NEWLINE* statement (NEWLINE+ statement)* NEWLINE*

statement: KEYWORD:redi{return} expr?
	     : KEYWORD:continua{continue}
		 : KEYWORD:confringe{break}
		 : expr

expr: KEYWORD:sino(var) IDENTIFIER EQ expr
    : comp-expr ((KEYWORD:et{and}|KEYWORD:aut{or}) comp-expr)*

comp-expr: non(not) comp-expr
         : arith-expr ((EE|LT|GT|LTE|GTE) arith-expr)*

arith-expr: term ((PLUS|MINUS) term)*

term: factor ((MUL|DIV) factor)*

factor: (PLUS|MINUS) factor
      : power

power: call (POW factor)*

call: atom (LPAREN (expr (COMMA expr)*)? RPAREN)?

atom: INT|FLOAT|STRING|IDENTIFIER
    : LPAREN expr RPAREN
    : list-expr
    : if-expr
    : for-expr
    : while-expr
    : func-def

list-expr: LSQUARE (expr (COMMA expr)*)? RSQUARE

if-expr: KEYWORD:si{if} expr KEYWORD:ergo{then}
       (statement if-expr-b|if-expr-c?)
       (NEWLINE statements KEYWORD:finis{end}|if-expr-b|if-expr-c)

if-expr-b: KEYWORD:alioquinsi{elif} expr KEYWORD:ergo{then}
         (statement if-expr-b|if-expr-c?)
         | (NEWLINE statements KEYWORD:finis{end}|if-expr-b|if-expr-c)

if-expr-c: KEYWORD:alioquin{else}
         statement
         | (NEWLINE statements KEYWORD:finis{end})

for-expr: KEYWORD:enim{for} IDENTIFIER EQ expr KEYWORD:ad{to} expr 
        (KEYWORD:gradus{step} expr)? KEYWORD:ergo{then}
        statement
        | (NEWLINE statements KEYWORD:finis{end})

while-expr: KEYWORD:dum{while} expr KEYWORD:ergo{then}
          statement
          | (NEWLINE statements KEYWORD:finis{end})

func-def: KEYWORD:opus{fun} IDENTIFIER?
        LPAREN (IDENTIFIER (COMMA IDENTIFIER)*)? RPAREN
        (ARROW expr)
        | (NEWLINE statements KEYWORD:finis{end})"""
        )
    elif help_num == "3":
        print('\nscribe(value_to_print) -> print\ninitus() -> input\npurgo() -> clear\nest_numerus(value_to_check) -> is_number\nest_filum(value_to_check) -> is_string\nest_album(value_to_check) -> is_list')
        print('est_opus(value_to_check) -> is_function\nadde(value_to_add) -> append\nremove(value_to_remove) -> pop\nextende(list_to_extend) -> extend\nlongitudo(value_to_check) -> length\ncurre(file_to_run) -> run')


#######################################
# Run Script Function
#######################################


def run_script(fn, script):
    result, error = root.run(fn, script)
    if error:
        print(error.as_string())
    elif result:
        if len(result.elements) == 1:
            print(repr(result.elements[0]))
        else:
            print(repr(result))


#######################################
# Run File from command line or take input
#######################################

if len(sys.argv) > 1:
    try:
        fn = sys.argv[1]
        with open(fn, "r") as f:
            script = f.read()
        run_script(fn, script)
    except FileNotFoundError as e:
        print(f"Can't open file {fn}: No such file")
    except UnicodeDecodeError as e:
        print(f"Can't open file {fn}: Invalid file format")
else:
    time = get_time()
    print(
        f"Celeritas versio unum (defalta, {time})\nScribe 'auxilium' auxilio")
    while True:
        text = input('>>> ')
        if text.strip() == "":
            continue
        if text == "auxilium":
            help_menu()
            continue
        run_script("<stdin>", text)
