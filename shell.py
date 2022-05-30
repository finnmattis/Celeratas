from datetime import datetime
import root
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

print(f"Celeritas versio unum (defalta, {time})\nScribe 'auxilium' auxilio")

while True:
    text = input('>>> ')
    if text.strip() == "":
        continue
    if text == "auxilium":
        print("This is a help menu!")
        continue
    result, error = root.run('<stdin>', text)

    if error:
        print(error.as_string())
    elif result:
        if len(result.elements) == 1:
            print(repr(result.elements[0]))
        else:
            print(repr(result))
