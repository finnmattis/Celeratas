#####################################
# IMPORTS
#####################################

from Celeratas.helper.errors import TypingError
from Celeratas.interpreter.Context import Context
from Celeratas.interpreter.RTResult import RTResult
from Celeratas.interpreter.SymbolTable import SymbolTable
from Celeratas.interpreter.values.Value import Value

#####################################
# BASE FUNCTION
#####################################


class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, func_args, input_args):

        res = RTResult()

        if len(input_args) > len(func_args):
            return res.failure(TypingError(
                self.pos_start, self.pos_end,
                f"{len(input_args) - len(func_args)} too many args passed into {self.name}()",
                self.context
            ))

        pos_args = [i for i in func_args if i[1] is None]

        if len(input_args) < len(pos_args):
            return res.failure(TypingError(
                self.pos_start, self.pos_end,
                f"{len(pos_args) - len(input_args)} too few args passed into {self}()",
                self.context
            ))

        return res.success(None)

    def populate_args(self, func_args, input_args, exec_ctx):

        for arg_idx, arg in enumerate(func_args):
            arg_name = arg[0]
            arg_value = arg[1]

            if arg_name in input_args:
                input_arg_value = input_args[arg_name]
                input_arg_value.set_context(exec_ctx)
                exec_ctx.symbol_table.set(arg_name, input_arg_value)
            elif arg_idx in input_args:
                input_arg_value = input_args[arg_idx]
                input_arg_value.set_context(exec_ctx)
                exec_ctx.symbol_table.set(arg_name, input_arg_value)
            else:
                arg_value.set_context(exec_ctx)
                exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RTResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return():
            return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)
