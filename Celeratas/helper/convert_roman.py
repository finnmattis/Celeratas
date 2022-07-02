#######################################
# IMPORTS
#######################################

import re

#######################################
# LOOKUP
#######################################

lookup = [
    (1000, 'M'),
    (900, 'CM'),
    (500, 'D'),
    (400, 'CD'),
    (100, 'C'),
    (90, 'XC'),
    (50, 'L'),
    (40, 'XL'),
    (10, 'X'),
    (9, 'IX'),
    (5, 'V'),
    (4, 'IV'),
    (1, 'I'),
]

#######################################
# Functions
#######################################


def toRoman(number):
    if isinstance(number, float):
        if number.is_integer():
            number = int(number)
        else:
            before_dot, after_dot = str(number).split(".")
            before_dot, after_dot = toRoman(
                int(before_dot)), toRoman(int(after_dot))
            return f"{before_dot}.{after_dot}"
    if number < 0:
        number = toRoman(number * -1)
        return f"-{number}"

    res = ''
    for (n, roman) in lookup:
        (d, number) = divmod(number, n)
        res += roman * d
    return res


def toNum(numeral):
    valid = bool(re.search(
        r"^-?M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})(\..M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))?$", numeral))
    if not valid:
        return None

    if "-" in numeral:
        numeral = toNum(numeral[1:])
        return numeral * -1

    if "." in numeral:
        before_dot, after_dot = numeral.split(".")
        before_dot, after_dot = toNum(before_dot), toNum(after_dot)
        if before_dot is None or after_dot is None:
            return None
        return float(f"{before_dot}.{after_dot}")

    res = 0
    numeral = numeral.replace("IV", "IIII").replace("IX", "VIIII")
    numeral = numeral.replace("XL", "XXXX").replace("XC", "LXXXX")
    numeral = numeral.replace("CD", "CCCC").replace("CM", "DCCCC")
    for char in numeral:
        for n in lookup:
            if char == n[1]:
                res += n[0]
    return res
