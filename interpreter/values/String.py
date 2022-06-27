#######################################
# IMPORTS
#######################################

from interpreter.values.Value import Value
from interpreter.values import Bool, Number

#######################################
# STRING
#######################################


class String(Value):
    def __init__(self, node, value, length):
        super().__init__()
        self.node = node
        self.value = value
        self.length = length

        self.attributes = {"length": length}

    def added_to(self, other):
        if isinstance(other, String):
            return String(self.components + other.components).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return String(self.components * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_eq(self, other):
        if isinstance(other, String):
            return Bool(self.components == other.components), None
        else:
            return None, Value.illegal_operation(self, other)

    def is_true(self):
        return len(self.components) > 0

    def copy(self):
        from interpreter.Interpreter import Interpreter
        interpreter = Interpreter()
        new_value = interpreter.visit(self.node, self.context)

        copy = new_value.value
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'"{self.value}"'
