#####################################
# IMPORTS
#####################################

import os

from Celeratas.helper.errors import IndexingError, RTError, TypingError
from Celeratas.interpreter.RTResult import RTResult
from Celeratas.interpreter.values import Bool, List, Number, String

from .BaseFunction import BaseFunction

#####################################
# BUILT IN FUNCTIONS
#####################################


class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args, _):
        res = RTResult()
        exec_ctx = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(
            method.arg_names, args, exec_ctx))
        if res.should_return():
            return res

        return_value = res.register(method(exec_ctx))
        if res.should_return():
            return res
        return res.success(return_value)

    def no_visit_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined')

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<built-in function {self.name}>"

    #####################################

    def execute_print(self, exec_ctx):
        print(str(exec_ctx.symbol_table.get('value')))
        return RTResult().success(None)
    execute_print.arg_names = [('value', None)]

    def execute_input(self, exec_ctx):
        text = input()
        return RTResult().success(String(text))
    execute_input.arg_names = []

    def execute_clear(self, exec_ctx):
        os.system('cls' if os.name == 'nt' else 'clear')
        return RTResult().success(None)
    execute_clear.arg_names = []

    def execute_is_number(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
        return RTResult().success(Bool(True) if is_number else Bool(False))
    execute_is_number.arg_names = [('value', None)]

    def execute_is_string(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
        return RTResult().success(Bool(True) if is_number else Bool(False))
    execute_is_string.arg_names = [("value", None)]

    def execute_is_list(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), List)
        return RTResult().success(Bool(True) if is_number else Bool(False))
    execute_is_list.arg_names = [("value", None)]

    def execute_is_function(self, exec_ctx):
        is_number = isinstance(
            exec_ctx.symbol_table.get("value"), BaseFunction)
        return RTResult().success(Bool(True) if is_number else Bool(False))
    execute_is_function.arg_names = [("value", None)]

    def execute_append(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        value = exec_ctx.symbol_table.get("value")

        if not isinstance(list_, List):
            return RTResult().failure(TypingError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        list_.elements.append(value)
        return RTResult().success(None)
    execute_append.arg_names = [("list", "value")]

    def execute_pop(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        index = exec_ctx.symbol_table.get("index")

        if not isinstance(list_, List):
            return RTResult().failure(TypingError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        if not isinstance(index, Number):
            return RTResult().failure(TypingError(
                self.pos_start, self.pos_end,
                "Second argument must be number",
                exec_ctx
            ))

        try:
            element = list_.elements.pop(index.value)
        except IndexError:
            return RTResult().failure(IndexingError(
                self.pos_start, self.pos_end,
                'Element at this index could not be removed from list because index is out of bounds',
                exec_ctx
            ))
        return RTResult().success(element)
    execute_pop.arg_names = [("list", None), ("index", None)]

    def execute_extend(self, exec_ctx):
        listA = exec_ctx.symbol_table.get("listA")
        listB = exec_ctx.symbol_table.get("listB")

        if not isinstance(listA, List):
            return RTResult().failure(TypingError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        if not isinstance(listB, List):
            return RTResult().failure(TypingError(
                self.pos_start, self.pos_end,
                "Second argument must be list",
                exec_ctx
            ))

        listA.elements.extend(listB.elements)
        return RTResult().success(None)
    execute_extend.arg_names = [("listA", None), ("listB", None)]

    def execute_len(self, exec_ctx):
        input_ = exec_ctx.symbol_table.get("input")

        if not isinstance(input_, List) and not isinstance(input_, String):
            return RTResult().failure(TypingError(
                self.pos_start, self.pos_end,
                "Argument must be list or string",
                exec_ctx
            ))

        return RTResult().success(Number(len(input_.elements if isinstance(input_, List) else input_.value)))
    execute_len.arg_names = [("input", None)]

    def execute_run(self, exec_ctx):
        fn = exec_ctx.symbol_table.get("fn")

        if not isinstance(fn, String):
            return RTResult().failure(TypingError(
                self.pos_start, self.pos_end,
                "Second argument must be string",
                exec_ctx
            ))

        fn = fn.value

        try:
            with open(fn, "r") as f:
                script = f.read()
        except Exception:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                f"Failed to load script \"{fn}\"",
                exec_ctx
            ))

        # Need the import here to avoid circular import
        from Celeratas.shell import run_script
        _, error = run_script(fn, script)

        if error:
            return RTResult().failure(TypingError(
                self.pos_start, self.pos_end,
                f"Failed to finish executing script \"{fn}\"\n" + error.as_string(),
                exec_ctx
            ))

        return RTResult().success(None)
    execute_run.arg_names = [("fn", None)]
