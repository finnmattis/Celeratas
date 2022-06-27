#!/usr/bin/python3

#######################################
# IMPORTS
#######################################

import sys
from datetime import datetime

import root.root as root


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
            with open("helper/grammar.txt", "r") as grammar:
                print(grammar.read())
        elif help_num == "3":
            print('\nscribe(value_to_print) -> print\ninitus() -> input\npurgo() -> clear\nest_numerus(value_to_check) -> is_number\nest_filum(value_to_check) -> is_string\nest_album(value_to_check) -> is_list')
            print('est_opus(value_to_check) -> is_function\nadde(value_to_add) -> append\nremove(value_to_remove) -> pop\nextende(list_to_extend) -> extend\nlongitudo(value_to_check) -> length\ncurre(file_to_run) -> run')

    #######################################
    # RUN SCRIPT FUNCTION
    #######################################

    def run_script(self, fn, script):
        result, error = root.run(fn, script)
        if error:
            print(error.as_string())
        elif result:
            result.elements = [x for x in result.elements if repr(x) != "None"]
            if len(result.elements) == 0:
                pass
            elif len(result.elements) == 1:
                print(repr(result.elements[0]))
            else:
                print(repr(result))

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
                    self.run_script(fn, script)
                except FileNotFoundError:
                    print(f"Can't open file {fn}: No such file")
                except UnicodeDecodeError:
                    print(f"Can't open file {fn}: Invalid file format")
            else:
                time = self.get_time()
                print(
                    f"Celeritas versio unum (defalta, {time})\nScribe 'auxilium' auxilio")
                while True:
                    text = input('>>> ')
                    if text.strip() == "":
                        continue
                    if text == "auxilium":
                        self.help_menu()
                        continue
                    self.run_script("<stdin>", text)
        except KeyboardInterrupt:
            print("\r", end="")
            print("Keyboard Interrupt")


if __name__ == '__main__':
    Shell = Shell()
