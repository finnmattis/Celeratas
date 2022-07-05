#######################################
# IMPORTS
#######################################

import Celeratas.helper.tokens as toks
from Celeratas.helper.errors import (AttrError, IndexingError, NamingError,
                                     RecursingError, RTError, TypingError)

from .RTResult import RTResult
from .values import Bool, Dict, Function, List, Number, Numeral, String

#######################################
# INTERPRETER
#######################################


class Interpreter:
    def __init__(self, recursion_depth):
        self.recursion_depth = recursion_depth

    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    ###################################

    def visit_NumberNode(self, node, context):
        return RTResult().success(
            Number(node.value).set_context(
                context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_NumeralNode(self, node, context):
        return RTResult().success(
            Numeral(node.value).set_context(
                context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_StringNode(self, node, context):
        res = RTResult()

        # Get the string
        string = ""
        for component in node.str_components:
            if isinstance(component, str):
                string += component
            else:
                result = self.visit(component, context)
                if result.error:
                    return res.failure(result.error)
                string += str(result.value)

        # Return the String Value Class
        return res.success(
            String(string).set_context(
                context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_BoolNode(self, node, context):
        return RTResult().success(
            Bool(node.value == "Verus").set_context(
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
        var_name_to_get = node.var_name_to_get
        value = context.symbol_table.get(var_name_to_get)
        idxes_to_get = node.idxes_to_get
        attrs_to_get = node.attrs_to_get

        if not value:
            return res.failure(NamingError(
                node.pos_start, node.pos_end,
                f"'{var_name_to_get}' is not defined",
                context
            ))

        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)

        # Check if it is not here before loop because it won't check a value that is from an index
        if idxes_to_get and not isinstance(value, List) and not isinstance(value, Dict) and not isinstance(value, String):
            return res.failure(IndexingError(
                node.pos_start, node.pos_end,
                "Can only get idx of list, dict, or string",
                context
            ))

        for idx_to_get in idxes_to_get:
            idx_to_get = res.register(self.visit(idx_to_get, context))
            idx_to_get = idx_to_get.value

            # need to get the value of the RTResult and then the Number class
            # Check if list:
            if isinstance(value, List):
                if not isinstance(idx_to_get, int):
                    return res.failure(IndexingError(
                        node.pos_start, node.pos_end,
                        'List index must be an int',
                        context
                    ))
                # If first statement is false, second will not evaluate
                if isinstance(value.elements, list) and idx_to_get < len(value.elements):
                    value.elements = value.elements[idx_to_get]
                    # If list in list:
                    if isinstance(value.elements, List):
                        value.elements = value.elements.elements
                    else:
                        value = value.elements
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
                        'String index must be an int',
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
                    'Index out of bounds',
                    context
                ))

        for attr_to_get in attrs_to_get:
            value_attr = value.attributes.get(attr_to_get, None)
            if value_attr is None:
                return res.failure(AttrError(
                    node.pos_start, node.pos_end,
                    f"'{var_name_to_get}' does not have the attribute '{attr_to_get}'",
                    context
                ))

            value = value_attr
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        assign_type = node.assign_type

        if len(node.vars_to_set) != len(node.values_to_set):
            return res.failure(TypingError(
                node.pos_start, node.pos_end,
                'Must have the same number of variables and values',
                context
            ))

        for var, value in zip(node.vars_to_set, node.values_to_set):
            value = res.register(self.visit(value, context))
            var_name = var[0]
            idxes_to_change = var[1]

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

                element_to_change = var_to_change

                for for_idx, idx_to_change in enumerate(idxes_to_change):
                    if isinstance(element_to_change, List):
                        if idx_to_change.value > len(element_to_change.elements) - 1:
                            return res.failure(IndexingError(
                                node.pos_start, node.pos_end,
                                'List index out of bounds',
                                context
                            ))
                        if for_idx == len(idxes_to_change) - 1:
                            element_to_change.elements[idx_to_change.value] = value
                        else:
                            element_to_change = element_to_change.elements[idx_to_change.value]
                    elif isinstance(element_to_change, Dict) or (hasattr(element_to_change, "elements") and isinstance(element_to_change.elements, Dict)):
                        if for_idx == len(idxes_to_change) - 1:
                            element_to_change.key_pairs[idx_to_change.value] = value
                        else:
                            element_to_change = element_to_change.key_pairs[idx_to_change.value]
                    else:
                        return res.failure(IndexingError(
                            node.pos_start, node.pos_end,
                            f'Variable must be a list or dict not \'{type(element_to_change).__name__}\' in order to set a specific index',
                            context
                        ))

                value = var_to_change

            if assign_type.type != "EQ":
                error = None
                old_value = context.symbol_table.get(var_name)

                if old_value is None:
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

        if node.op_tok.type == toks.TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == toks.TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == toks.TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == toks.TT_DIV:
            result, error = left.dived_by(right)
        elif node.op_tok.type == toks.TT_POW:
            result, error = left.powed_by(right)
        elif node.op_tok.type == toks.TT_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == toks.TT_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_tok.type == toks.TT_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == toks.TT_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == toks.TT_LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_tok.type == toks.TT_GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_tok.matches(toks.TT_KEYWORD, 'et'):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(toks.TT_KEYWORD, 'aut'):
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

        if node.op_tok.type == toks.TT_MINUS:
            number, error = number.multed_by(Number(-1))
        elif node.op_tok.matches(toks.TT_KEYWORD, 'non'):
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

            if condition_value is None:
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

        should_except = not node.except_name or node.except_name.value == "Exception" or try_body.error.error_name == node.except_name.value
        if try_body.error and node.except_body and should_except:
            if node.except_as:
                context.symbol_table.set(
                    node.except_as.value, String(try_body.error.details))

            res.register(self.visit(node.except_body, context))
            if res.error:
                return res

            if node.except_as:
                context.symbol_table.remove(node.except_as.value)
        elif try_body.error is None:
            try_body = res.register(try_body)
            if res.error:
                return res

        return res.success(None if node.should_return_null else try_body)

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

        if start_value is None:
            return res.failure(RTError(
                node.start_value_node.pos_start, node.start_value_node.pos_end,
                'Expression does not have a value',
                context
            ))

        i = start_value.value

        if step_value.value >= 0:
            def condition():
                return i < end_value.value
        else:
            def condition():
                return i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name, Number(i))
            i += step_value.value

            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_should_continue and res.loop_should_break:
                return res

            if res.loop_should_continue:
                continue

            if res.loop_should_break:
                break

            elements.append(value)

        context.symbol_table.remove(node.var_name)
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

            if condition_value is None:
                return res.failure(RTError(
                    node.condition_node.pos_start, node.condition_node.pos_end,
                    'Conditional can not be evaluated',
                    context
                ))

            if not condition_value.is_true():
                break

            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_should_continue and res.loop_should_break:
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

        func_name = node.func_name if node.func_name else None
        body_node = node.body_node
        args = []
        for arg_name, arg_value in node.args:
            if arg_value is None:
                args.append((arg_name, arg_value))
            else:
                arg_value = res.register(self.visit(arg_value, context))
                if res.should_return():
                    return res
                args.append((arg_name, arg_value))

        func_value = Function(func_name, body_node, args, node.should_auto_return).set_context(
            context).set_pos(node.pos_start, node.pos_end)

        if node.func_name:
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)

    def visit_CallNode(self, node, context):

        if self.recursion_depth > 100:
            return RTResult().failure(RecursingError(
                node.pos_start, node.pos_end,
                'Recursion depth exceeded',
                context
            ))

        res = RTResult()
        args = {}

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.should_return():
            return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_key, arg_value in node.arg_nodes.items():
            arg_value = res.register(self.visit(arg_value, context))
            if res.should_return():
                return res

            args[arg_key] = arg_value

        return_value = res.register(value_to_call.execute(args, self.recursion_depth))
        if res.should_return():
            return res
        if return_value is None:
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
