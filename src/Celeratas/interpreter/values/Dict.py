#######################################
# IMPORTS
#######################################

from .Value import Value

#######################################
# DICT
#######################################


class Dict(Value):
    def __init__(self, key_pairs):
        super().__init__()
        self.key_pairs = key_pairs

    def copy(self):
        copy = Dict(self.key_pairs)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.set_context)
        return copy

    def __str__(self):
        return str(self.key_pairs)

    def __repr__(self):
        return str(self.key_pairs)
