#######################################
# IMPORTS
#######################################

import math
import os

from attr import attr

from helper.convert_roman import *
from helper.tokens import *
from helper.errors import DivisionByZeroError, IndexingError, NamingError, AttrError, RTError, TypingError

#######################################
# RUNTIME RESULT
#######################################


class RTResult:
    def __init__(self):
        self.reset()

    def reset(self):
        self.value = None
        self.error = None
        self.func_return_value = None
        self.loop_should_continue = False
        self.loop_should_break = False

    def register(self, res):
        self.error = res.error
        self.func_return_value = res.func_return_value
        self.loop_should_continue = res.loop_should_continue
        self.loop_should_break = res.loop_should_break
        return res.value

    def success(self, value):
        self.reset()
        self.value = value
        return self

    def success_return(self, value):
        self.reset()
        self.func_return_value = value
        return self

    def success_continue(self):
        self.reset()
        self.loop_should_continue = True
        return self

    def success_break(self):
        self.reset()
        self.loop_should_break = True
        return self

    def failure(self, error):
        self.reset()
        self.error = error
        return self

    def should_return(self):
        # Note: this will allow you to continue and break outside the current function
        return (
            self.error or
            self.func_return_value or
            self.loop_should_continue or
            self.loop_should_break
        )

#######################################
# VALUES
#######################################


class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()
        self.attributes = {}

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multed_by(self, other):
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        return None, self.illegal_operation(other)

    def powed_by(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_ne(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gte(self, other):
        return None, self.illegal_operation(other)

    def anded_by(self, other):
        return None, self.illegal_operation(other)

    def ored_by(self, other):
        return None, self.illegal_operation(other)

    def notted(self, other):
        return None, self.illegal_operation(other)

    def execute(self, args):
        return RTResult().failure(self.illegal_operation())

    def copy(self):
        raise Exception('No copy method defined')

    def is_true(self):
        return False

    def illegal_operation(self, other=None):
        if not other:
            other = self
        return TypingError(
            self.pos_start, other.pos_end,
            f'Illegal operation between {type(self).__name__} and {type(other).__name__}',
            self.context
        )


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
            return Bool(self.value and other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def ored_by(self, other):
        if isinstance(other, Number) or isinstance(other, Numeral):
            return Bool(self.value or other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def notted(self):
        return Bool(True if self.value == 0 else False).set_context(self.context), None

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


Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)
Number.math_PI = Number(math.pi)


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


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.attributes = {"length": len(value)}

    def added_to(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_eq(self, other):
        if isinstance(other, String):
            return Number(int(self.value == other.value)), None
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


class Bool(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def copy(self):
        copy = Bool(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def get_comparison_eq(self, other):
        if isinstance(other, Bool):
            return Bool(self.value == other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_ne(self, other):
        if isinstance(other, Bool):
            return Bool(self.value != other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lt(self, other):
        if isinstance(other, Bool):
            return Bool(self.value < other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gt(self, other):
        if isinstance(other, Bool):
            return Bool(self.value > other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lte(self, other):
        if isinstance(other, Bool):
            return Bool(self.value <= other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gte(self, other):
        if isinstance(other, Bool):
            return Bool(self.value >= other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def anded_by(self, other):
        if isinstance(other, Bool):
            return Bool(self.value and other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def ored_by(self, other):
        if isinstance(Bool):
            return Bool(self.value or other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def notted(self):
        return Bool(not self.value).set_context(self.context), None

    def is_true(self):
        return self.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)


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


class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        res = RTResult()

        if len(args) > len(arg_names):
            return res.failure(TypingError(
                self.pos_start, self.pos_end,
                f"{len(args) - len(arg_names)} too many args passed into {self.name}()",
                self.context
            ))

        if len(args) < len(arg_names):
            return res.failure(TypingError(
                self.pos_start, self.pos_end,
                f"{len(arg_names) - len(args)} too few args passed into {self}()",
                self.context
            ))

        return res.success(None)

    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RTResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return():
            return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)


class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, should_auto_return):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_auto_return = should_auto_return

    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()

        res.register(self.check_and_populate_args(
            self.arg_names, args, exec_ctx))
        if res.should_return():
            return res

        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.should_return() and res.func_return_value == None:
            return res

        ret_value = (
            value if self.should_auto_return else None) or res.func_return_value or None
        return res.success(ret_value)

    def copy(self):
        copy = Function(self.name, self.body_node,
                        self.arg_names, self.should_auto_return)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"


class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
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
    execute_print.arg_names = ['value']

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
        return RTResult().success(Number.true if is_number else Number.false)
    execute_is_number.arg_names = ["value"]

    def execute_is_string(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
        return RTResult().success(Number.true if is_number else Number.false)
    execute_is_string.arg_names = ["value"]

    def execute_is_list(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), List)
        return RTResult().success(Number.true if is_number else Number.false)
    execute_is_list.arg_names = ["value"]

    def execute_is_function(self, exec_ctx):
        is_number = isinstance(
            exec_ctx.symbol_table.get("value"), BaseFunction)
        return RTResult().success(Number.true if is_number else Number.false)
    execute_is_function.arg_names = ["value"]

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
    execute_append.arg_names = ["list", "value"]

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
        except:
            return RTResult().failure(IndexingError(
                self.pos_start, self.pos_end,
                'Element at this index could not be removed from list because index is out of bounds',
                exec_ctx
            ))
        return RTResult().success(element)
    execute_pop.arg_names = ["list", "index"]

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
    execute_extend.arg_names = ["listA", "listB"]

    def execute_len(self, exec_ctx):
        input_ = exec_ctx.symbol_table.get("input")

        if not isinstance(input_, List) and not isinstance(input_, String):
            return RTResult().failure(TypingError(
                self.pos_start, self.pos_end,
                "Argument must be list or string",
                exec_ctx
            ))

        return RTResult().success(Number(len(input_.elements if isinstance(input_, List) else input_.value)))
    execute_len.arg_names = ["input"]

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
        except Exception as e:
            return RTResult().failure(TypingError(
                self.pos_start, self.pos_end,
                f"Failed to load script \"{fn}\"\n" + str(e),
                exec_ctx
            ))

        # Need the import here to avoid circular import
        from main.root import run
        _, error = run(fn, script)

        if error:
            return RTResult().failure(TypingError(
                self.pos_start, self.pos_end,
                f"Failed to finish executing script \"{fn}\"\n" +
                error.as_string(),
                exec_ctx
            ))

        return RTResult().success(None)
    execute_run.arg_names = ["fn"]


BuiltInFunction.print = BuiltInFunction("print")
BuiltInFunction.input = BuiltInFunction("input")
BuiltInFunction.clear = BuiltInFunction("clear")
BuiltInFunction.is_number = BuiltInFunction("is_number")
BuiltInFunction.is_string = BuiltInFunction("is_string")
BuiltInFunction.is_list = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append = BuiltInFunction("append")
BuiltInFunction.pop = BuiltInFunction("pop")
BuiltInFunction.extend = BuiltInFunction("extend")
BuiltInFunction.len = BuiltInFunction("len")
BuiltInFunction.run = BuiltInFunction("run")

#######################################
# CONTEXT
#######################################


class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None

#######################################
# SYMBOL TABLE
#######################################


class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]

#######################################
# INTERPRETER
#######################################


class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    ###################################

    def visit_NumberNode(self, node, context):
        return RTResult().success(
            Number(node.tok.value).set_context(
                context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_NumeralNode(self, node, context):
        return RTResult().success(
            Numeral(node.tok.value).set_context(
                context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_StringNode(self, node, context):
        return RTResult().success(
            String(node.tok.value).set_context(
                context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_BoolNode(self, node, context):
        return RTResult().success(
            Bool(True if node.tok.value == "True" else False).set_context(
                context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_ListNode(self, node, context):
        res = RTResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(res.register(self.visit(element_node, context)))
            if res.should_return():
                return res

        return res.success(
            List(elements).set_context(context).set_pos(
                node.pos_start, node.pos_end)
        )

    def visit_DictNode(self, node, context):
        res = RTResult()
        keypairs = {}

        for key, value in node.key_pairs.items():
            key = res.register(self.visit(key, context))

            if res.error:
                return res

            if isinstance(key, List):
                return res.failure(TypingError(
                    key.pos_start, key.pos_end,
                    "Key cannot be a list",
                    context
                ))

            value = res.register(self.visit(value, context))
            if res.error:
                return res

            keypairs[key.value] = value

        return res.success(Dict(keypairs).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)
        idxes_to_get = node.idxes_to_get
        attr_to_get = node.attr_to_get

        if not value:
            return res.failure(NamingError(
                node.pos_start, node.pos_end,
                f"'{var_name}' is not defined",
                context
            ))

        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)

        for idx_to_get in idxes_to_get:
            idx_to_get = res.register(self.visit(idx_to_get, context))
            idx_to_get = idx_to_get.value

            # need to get the value of the RTResult and then the Number class
            # Check if list:
            if isinstance(value, List):
                if not isinstance(idx_to_get, int):
                    return res.failure(IndexingError(
                        node.pos_start, node.pos_end,
                        f'List index must be an int',
                        context
                    ))
                # If first statement is false, second will not evaluate
                if isinstance(value.elements, list) and idx_to_get < len(value.elements):
                    value.elements = value.elements[idx_to_get]
                    # If list in list:
                    if isinstance(value.elements, List):
                        value.elements = value.elements.elements
                else:
                    return res.failure(IndexingError(
                        node.pos_start, node.pos_end,
                        'List index out of bounds',
                        context
                    ))
            elif isinstance(value, Dict):
                found = False

                for key in value.key_pairs:
                    if key == idx_to_get:
                        value = value.key_pairs[key]
                        found = True
                        break

                if not found:
                    return res.failure(IndexingError(
                        node.pos_start, node.pos_end,
                        'Dict index out of bounds',
                        context
                    ))
            elif isinstance(value, String):
                if not isinstance(idx_to_get, int):
                    return res.failure(IndexingError(
                        node.pos_start, node.pos_end,
                        f'String index must be an int',
                        context
                    ))
                if idx_to_get < len(value.value):
                    value.value = value.value[idx_to_get]
                else:
                    return res.failure(IndexingError(
                        node.pos_start, node.pos_end,
                        'String index out of bounds',
                        context
                    ))
            else:
                return res.failure(TypingError(
                    node.pos_start, node.pos_end,
                    'Can only get idx of list, dict, or string',
                    context
                ))
        if attr_to_get:
            if value.elements:
                value = value.elements

            value_attr = value.attributes.get(attr_to_get, None)
            if value_attr == None:
                return res.failure(AttrError(
                    node.pos_start, node.pos_end,
                    f"'{var_name}' does not have the attribute '{attr_to_get}'",
                    context
                ))

            value_attr = Number(value_attr)
            return res.success(value_attr)
        # idxes to get will have elements but value will no elements if value is a dict
        return res.success(value.elements if hasattr(value, "elements") else value)

    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        idxes_to_change = node.idxes_to_change
        assign_type = node.assign_type

        value = res.register(self.visit(node.value_node, context))
        if res.should_return():
            return res

        if idxes_to_change:
            if var_name not in context.symbol_table.symbols:
                return res.failure(NamingError(
                    node.pos_start, node.pos_end,
                    f"'{var_name}' is not defined",
                    context
                ))

            var_to_change = context.symbol_table.get(var_name)

            if isinstance(var_to_change, List):
                element_to_change = var_to_change

                for for_idx, idx_to_change in enumerate(idxes_to_change):
                    if not isinstance(element_to_change, List) or idx_to_change.tok.value > len(element_to_change.elements) - 1:
                        return res.failure(IndexingError(
                            node.pos_start, node.pos_end,
                            'List index out of bounds',
                            context
                        ))

                    if for_idx == len(idxes_to_change) - 1:
                        element_to_change.elements[idx_to_change.tok.value] = value
                    else:
                        element_to_change = element_to_change.elements[idx_to_change.tok.value]
            elif isinstance(var_to_change, Dict):
                for for_idx, idx_to_change in enumerate(idxes_to_change):
                    if for_idx == len(idxes_to_change) - 1:
                        var_to_change.key_pairs[idx_to_change.tok.value] = value
                    else:
                        var_to_change = var_to_change.key_pairs[idx_to_change.tok.value]
            else:
                return res.failure(IndexingError(
                    node.pos_start, node.pos_end,
                    'Variable must be a list or dict in order to set a specific index',
                    context
                ))

            value = var_to_change

        if assign_type.type != "EQ":
            error = None
            old_value = context.symbol_table.get(var_name)

            if old_value == None:
                return res.failure(NamingError(
                    node.pos_start, node.pos_end,
                    f"'{var_name}' is not defined",
                    context
                ))

            if assign_type.type == "PLUS_EQ":
                value, error = old_value.added_to(value)
            elif assign_type.type == "MIN_EQ":
                value, error = old_value.subbed_by(value)
            elif assign_type.type == "MUL_EQ":
                value, error = old_value.multed_by(value)
            elif assign_type.type == "DIV_EQ":
                value, error = old_value.dived_by(value)

            if error:
                return res.failure(error)

        context.symbol_table.set(var_name, value)
        return res.success(None)

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.should_return():
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.should_return():
            return res

        if node.op_tok.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == TT_DIV:
            result, error = left.dived_by(right)
        elif node.op_tok.type == TT_POW:
            result, error = left.powed_by(right)
        elif node.op_tok.type == TT_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == TT_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_tok.type == TT_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == TT_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == TT_LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_tok.type == TT_GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_tok.matches(TT_KEYWORD, 'et'):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(TT_KEYWORD, 'aut'):
            result, error = left.ored_by(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.should_return():
            return res

        error = None

        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))
        elif node.op_tok.matches(TT_KEYWORD, 'non'):
            number, error = number.notted()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_IfNode(self, node, context):
        res = RTResult()

        for condition, expr, should_return_null in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.should_return():
                return res

            if condition_value == None:
                return res.failure(RTError(
                    node.pos_start, node.pos_end,
                    'Conditional can not be evaluated',
                    context
                ))

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.should_return():
                    return res
                return res.success(None if should_return_null else expr_value)

        if node.else_case:
            expr, should_return_null = node.else_case
            expr_value = res.register(self.visit(expr, context))
            if res.should_return():
                return res
            return res.success(None if should_return_null else expr_value)

        return res.success(None)

    def visit_TryNode(self, node, context):
        res = RTResult()
        try_body = self.visit(node.try_body, context)

        if node.except_name and node.except_name.value not in ["Exception", "TypeError", "NameError", "IndexError", "ZeroDivisionError"]:
            return res.failure(NamingError(
                node.except_name.pos_start, node.except_name.pos_end,
                'Exception type not supported',
                context
            ))

        if try_body.error and node.except_body and (not node.except_name or node.except_name.value == "Exception" or try_body.error.error_name == node.except_name.value):
            if node.except_as:
                context.symbol_table.set(
                    node.except_as.value, String(try_body.error.details))

            res.register(self.visit(node.except_body, context))
            if res.error:
                return res

            if node.except_as:
                context.symbol_table.remove(node.except_as.value)
        elif try_body.error == None:
            try_body = res.register(try_body)
            if res.error:
                return res
        return res.success(None)

    def visit_ForNode(self, node, context):
        res = RTResult()
        elements = []

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.should_return():
            return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.should_return():
            return res

        if node.step_value_node:
            step_value = res.register(
                self.visit(node.step_value_node, context))
            if res.should_return():
                return res
        else:
            step_value = Number(1)

        if start_value == None:
            return res.failure(RTError(
                node.start_value_node.pos_start, node.start_value_node.pos_end,
                'Expression does not have a value',
                context
            ))

        i = start_value.value

        if step_value.value >= 0:
            def condition(): return i < end_value.value
        else:
            def condition(): return i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value

            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False:
                return res

            if res.loop_should_continue:
                continue

            if res.loop_should_break:
                break

            elements.append(value)

        context.symbol_table.remove(node.var_name_tok.value)
        return res.success(
            None if node.should_return_null else
            List(elements).set_context(context).set_pos(
                node.pos_start, node.pos_end)
        )

    def visit_WhileNode(self, node, context):
        res = RTResult()
        elements = []

        while True:
            condition_value = res.register(
                self.visit(node.condition_node, context))
            if res.should_return():
                return res

            if condition_value == None:
                return res.failure(RTError(
                    node.condition_node.pos_start, node.condition_node.pos_end,
                    'Conditional can not be evaluated',
                    context
                ))

            if not condition_value.is_true():
                break

            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False:
                return res

            if res.loop_should_continue:
                continue

            if res.loop_should_break:
                break

            elements.append(value)

        return res.success(
            None if node.should_return_null else
            List(elements).set_context(context).set_pos(
                node.pos_start, node.pos_end)
        )

    def visit_FuncDefNode(self, node, context):
        res = RTResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        func_value = Function(func_name, body_node, arg_names, node.should_auto_return).set_context(
            context).set_pos(node.pos_start, node.pos_end)

        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)

    def visit_CallNode(self, node, context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.should_return():
            return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.should_return():
                return res

        return_value = res.register(value_to_call.execute(args))
        if res.should_return():
            return res
        if return_value == None:
            return res.success(None)

        return_value = return_value.copy().set_pos(
            node.pos_start, node.pos_end).set_context(context)
        return res.success(return_value)

    def visit_ReturnNode(self, node, context):
        res = RTResult()

        if node.node_to_return:
            value = res.register(self.visit(node.node_to_return, context))
            if res.should_return():
                return res
        else:
            value = None

        return res.success_return(value)

    def visit_ContinueNode(self, node, context):
        return RTResult().success_continue()

    def visit_BreakNode(self, node, context):
        return RTResult().success_break()
