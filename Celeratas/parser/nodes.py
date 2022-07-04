class NumberNode:
    def __init__(self, value, pos_start, pos_end):
        self.value = value

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'{self.value}'


class NumeralNode:
    def __init__(self, value, pos_start, pos_end):
        self.value = value

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return self.value


class StringNode:
    def __init__(self, str_components, pos_start, pos_end):
        self.str_components = str_components

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'{self.str_components}'


class BoolNode:
    def __init__(self, value, pos_start, pos_end):
        self.value = value

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return self.value


class ListNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end


class DictNode:
    def __init__(self, key_pairs, pos_start, pos_end):
        self.key_pairs = key_pairs

        self.pos_start = pos_start
        self.pos_end = pos_end


class VarAccessNode:
    def __init__(self, var_name_to_get, idxes_to_get, attrs_to_get, pos_start, pos_end):
        self.var_name_to_get = var_name_to_get
        self.idxes_to_get = idxes_to_get
        self.attrs_to_get = attrs_to_get

        self.pos_start = pos_start
        self.pos_end = pos_end


class VarAssignNode:
    def __init__(self, vars_to_set, values_to_set, assign_type, pos_start, pos_end):
        self.vars_to_set = vars_to_set
        self.values_to_set = values_to_set
        self.assign_type = assign_type

        self.pos_start = pos_start
        self.pos_end = pos_end


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node, pos_start, pos_end):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class UnaryOpNode:
    def __init__(self, op_tok, node, pos_start, pos_end):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


class IfNode:
    def __init__(self, cases, else_case, pos_start, pos_end):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = pos_start
        self.pos_end = pos_end


class TryNode:
    def __init__(self, try_body, except_body, except_name, except_as, should_return_null, pos_start, pos_end):
        self.try_body = try_body
        self.except_body = except_body
        self.except_name = except_name
        self.except_as = except_as
        self.should_return_null = should_return_null

        self.pos_start = pos_start
        self.pos_end = pos_end


class ForNode:
    def __init__(self, var_name, start_value_node, end_value_node, step_value_node, body_node, should_return_null, pos_start, pos_end):
        self.var_name = var_name
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = pos_start
        self.pos_end = pos_end


class WhileNode:
    def __init__(self, condition_node, body_node, should_return_null, pos_start, pos_end):
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = pos_start
        self.pos_end = pos_end


class FuncDefNode:
    def __init__(self, func_name, args, body_node, should_auto_return, pos_start, pos_end):
        self.func_name = func_name
        self.args = args
        self.body_node = body_node
        self.should_auto_return = should_auto_return

        self.pos_start = pos_start
        self.pos_end = pos_end


class CallNode:
    def __init__(self, node_to_call, arg_nodes, pos_start, pos_end):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end


class ReturnNode:
    def __init__(self, node_to_return, pos_start, pos_end):
        self.node_to_return = node_to_return

        self.pos_start = pos_start
        self.pos_end = pos_end


class ContinueNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


class BreakNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end
