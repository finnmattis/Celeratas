#######################################
# IMPORTS
#######################################

from interpreter.values.Value import Value
from interpreter.values import Bool, Number
from parser.nodes import StringNode

#######################################
# STRING
#######################################


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

        self.attributes = {"length": len(value)}

    def added_to(self, other):
        if isinstance(other, String):
            return String(StringNode(self.node.str_components + other.node.str_components, self.pos_start, other.pos_end), self.value + other.value, self.length + other.length).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return String(StringNode(self.node.str_components * other.value, self.pos_start, other.pos_end), self.value * other.value, self.length * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_eq(self, other):
        if isinstance(other, String):
            return Bool(self.value == other.value), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_ne(self, other):
        if isinstance(other, String):
            return Bool(self.value != other.value), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lt(self, other):
        if isinstance(other, String):
            return Bool(self.value < other.value), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gt(self, other):
        if isinstance(other, String):
            return Bool(self.value > other.value), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lte(self, other):
        if isinstance(other, String):
            return Bool(self.value <= other.value), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gte(self, other):
        if isinstance(other, String):
            return Bool(self.value >= other.value), None
        else:
            return None, Value.illegal_operation(self, other)

    def is_true(self):
        return len(self.value) > 0

    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'"{self.value}"'
