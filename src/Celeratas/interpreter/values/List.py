#######################################
# IMPORTS
#######################################

from .Value import Value

#######################################
# LIST
#######################################


class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def copy(self):
        copy = List(self.elements)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __str__(self):
        return ", ".join([str(x) for x in self.elements])

    def __repr__(self):
        return f'[{", ".join([repr(x) for x in self.elements])}]'
