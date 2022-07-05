#######################################
# IMPORTS
#######################################

from Celeratas.helper.convert_roman import toRoman
from Celeratas.helper.errors import DivisionByZeroError

from .Bool import Bool
from .Value import Value

#######################################
# NUMBER
#######################################


class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, Number) or isinstance(other, Numeral):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def subbed_by(self, other):
        if isinstance(other, Number) or isinstance(other, Numeral):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Number) or isinstance(other, Numeral):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def dived_by(self, other):
        if isinstance(other, Number) or isinstance(other, Numeral):
            if other.value == 0:
                return None, DivisionByZeroError(
                    other.pos_start, other.pos_end,
                    'Division by zero',
                    self.context
                )

            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def powed_by(self, other):
        if isinstance(other, Number) or isinstance(other, Numeral):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_eq(self, other):
        if isinstance(other, Number) or isinstance(other, Numeral):
            return Bool(self.value == other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_ne(self, other):
        if isinstance(other, Number) or isinstance(other, Numeral):
            return Bool(self.value != other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lt(self, other):
        if isinstance(other, Number) or isinstance(other, Numeral):
            return Bool(self.value < other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gt(self, other):
        if isinstance(other, Number) or isinstance(other, Numeral):
            return Bool(self.value > other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lte(self, other):
        if isinstance(other, Number) or isinstance(other, Numeral):
            return Bool(self.value <= other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gte(self, other):
        if isinstance(other, Number) or isinstance(other, Numeral):
            return Bool(self.value >= other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def anded_by(self, other):
        if isinstance(other, Number) or isinstance(other, Numeral):
            return Number(self.value and other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def ored_by(self, other):
        if isinstance(other, Number) or isinstance(other, Numeral):
            return Number(self.value or other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def notted(self):
        return Bool(self.value == 0).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

#######################################
# NUMERAL
#######################################


class Numeral(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, Numeral) or isinstance(other, Number):
            return Numeral(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def subbed_by(self, other):
        if isinstance(other, Numeral) or isinstance(other, Number):
            return Numeral(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Numeral) or isinstance(other, Number):
            return Numeral(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def dived_by(self, other):
        if isinstance(other, Numeral) or isinstance(other, Number):
            if other.value == 0:
                return None, DivisionByZeroError(
                    other.pos_start, other.pos_end,
                    'Division by zero',
                    self.context
                )

            return Numeral(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def powed_by(self, other):
        if isinstance(other, Numeral) or isinstance(other, Number):
            return Numeral(self.value ** other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_eq(self, other):
        if isinstance(other, Numeral) or isinstance(other, Number):
            return Bool(self.value == other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_ne(self, other):
        if isinstance(other, Numeral) or isinstance(other, Number):
            return Bool(self.value != other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lt(self, other):
        if isinstance(other, Numeral) or isinstance(other, Number):
            return Bool(self.value < other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gt(self, other):
        if isinstance(other, Numeral) or isinstance(other, Number):
            return Bool(self.value > other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lte(self, other):
        if isinstance(other, Numeral) or isinstance(other, Number):
            return Bool(self.value <= other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gte(self, other):
        if isinstance(other, Numeral) or isinstance(other, Number):
            return Bool(self.value >= other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def anded_by(self, other):
        if isinstance(other, Numeral) or isinstance(other, Number):
            return Bool(self.value and other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def ored_by(self, other):
        if isinstance(other, Numeral) or isinstance(other, Number):
            return Bool(self.value or other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def notted(self):
        return Bool(True if self.value == 0 else False).set_context(self.context), None

    def copy(self):
        copy = Numeral(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __str__(self):
        return toRoman(round(self.value, 3)) if self.value != 0 else "nil"

    def __repr__(self):
        return toRoman(round(self.value, 3)) if self.value != 0 else "nil"
