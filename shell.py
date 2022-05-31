#######################################
# IMPORTS
#######################################

import sys
from datetime import datetime

import root

#######################################
# Date
#######################################

time = datetime.now().strftime("%b %d %y, %H:%M:%S")
time = time.replace("Jan", "Unus Martius")
time = time.replace("Feb", "Duo Martius")
time = time.replace("Mar", "Martius")
time = time.replace("Apr", "Aprilis")
time = time.replace("May", "Maius")
time = time.replace("Jun", "Junius")
time = time.replace("Jul", "Quintilis")
time = time.replace("Aug", "Sextilis")
# Don't need to replace Sep, Oct, Nov, or Dec bc they are the same in latin

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
else:
    print(
        f"Celeritas versio unum (defalta, {time})\nScribe 'auxilium' auxilio")
    while True:
        text = input('>>> ')
        if text.strip() == "":
            continue
        if text == "auxilium":
            print("Don't worry this menu isn't in latin!")
            continue
        run_script("<stdin>", text)
