#######################################
# IMPORTS
#######################################

from Celeratas.helper.tokens import *
from Celeratas.helper.errors import ExpectedItemError, InvalidSyntaxError, IndentError

from .nodes import *
from .ParseResult import ParseResult

#######################################
# PARSER
#######################################


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.indent_count = 0
        self.advance()

    def advance(self):
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok

    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def parse(self):
        res = self.statements()

        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Token cannot appear after previous tokens"
            ))
        return res

    def check_indent_amount(self):
        res = ParseResult()
        tab_count = 0

        # Check Tab count from tokens
        while True:
            if self.current_tok.type == TT_TAB:
                res.register_advancement()
                self.advance()
                tab_count += 1
            else:
                break

        # Check if greater than expected tab count
        if tab_count > self.indent_count:
            return None, res.failure(IndentError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Incorrect number of tabs!"))
        return tab_count, None

    ###################################

    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

        tab_amount, error = self.check_indent_amount()
        if error:
            res.register(error)
            return res

        if tab_amount < self.indent_count:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected Tab"))

        statement = res.register(self.statement())

        if res.error:
            return res

        statements.append(statement)
        more_statements = True

        while True:
            newline_count = 0
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()
                newline_count += 1

            tab_amount, error = self.check_indent_amount()

            if error:
                res.register(error)
                return res

            if tab_amount < self.indent_count:
                more_statements = False

            if not more_statements:
                break

            statement = res.try_register(self.statement())

            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue

            statements.append(statement)

        return res.success(ListNode(
            statements,
            pos_start,
            self.current_tok.pos_end.copy()
        ))

    def statement(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.matches(TT_KEYWORD, 'redi'):
            res.register_advancement()
            self.advance()

            expr = res.try_register(self.expr())
            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))

        if self.current_tok.matches(TT_KEYWORD, 'continua'):
            res.register_advancement()
            self.advance()
            return res.success(ContinueNode(pos_start, self.current_tok.pos_start.copy()))

        if self.current_tok.matches(TT_KEYWORD, 'confringe'):
            res.register_advancement()
            self.advance()
            return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))

        expr = res.register(self.expr())
        if res.error:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected expression"
            ))
        return res.success(expr)

    def expr(self, could_have_var_assign=True):
        res = ParseResult()

        if self.current_tok.type == TT_IDENTIFIER:
            var_names_to_set = []
            idxes_to_change = []
            pos_start = self.current_tok.pos_start.copy()

            while True:
                var_names_to_set.append(self.current_tok.value)

                res.register_advancement()
                self.advance()

                if not self.current_tok.type == TT_COMMA:
                    break

                res.register_advancement()
                self.advance()

                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(ExpectedItemError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected identifier"
                    ))

            while self.current_tok.type == TT_LSQUARE:
                res.register_advancement()
                self.advance()

                idxes_to_change.append(res.register(self.bin_op(
                    self.comp_expr, ((TT_KEYWORD, 'et'), (TT_KEYWORD, 'aut')))))

                if res.error:
                    return res

                res.register_advancement()
                self.advance()

            if self.current_tok.type not in [TT_EQ, TT_PLUS_EQ, TT_MIN_EQ, TT_MUL_EQ, TT_DIV_EQ]:
                self.reverse(res.advance_count)
            else:
                if could_have_var_assign == False:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Inappropriate Var Assign Node"
                    ))

                assign_type = self.current_tok

                res.register_advancement()
                self.advance()

                values = []

                while True:
                    values.append(res.register(
                        self.expr(could_have_var_assign=False)))

                    if res.error:
                        return res

                    if not self.current_tok.type == TT_COMMA:
                        break

                    res.register_advancement()
                    self.advance()

                return res.success(VarAssignNode(var_names_to_set, values, idxes_to_change, assign_type, pos_start, pos_end=values[-1].pos_end))

        node = res.register(self.bin_op(
            self.comp_expr, ((TT_KEYWORD, 'et'), (TT_KEYWORD, 'aut'))))

        if res.error:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected expression"
            ))

        return res.success(node)

    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, 'non'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))

        node = res.register(self.bin_op(
            self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))

        if res.error:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected expression"
            ))

        return res.success(node)

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def power(self):
        return self.bin_op(self.call, (TT_POW, ), self.factor)

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error:
            return res

        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(ExpectedItemError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ')' or expression"
                    ))

                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error:
                        return res

                if self.current_tok.type != TT_RPAREN:
                    return res.failure(ExpectedItemError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected ',' or ')'"
                    ))

                res.register_advancement()
                self.advance()
            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type == TT_NUMERAL:
            res.register_advancement()
            self.advance()
            return res.success(NumeralNode(tok))

        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type == TT_STRING:
            str_components = tok.value
            for val in str_components:
                if isinstance(val, list):
                    parser = Parser(val)
                    ast = parser.expr()
                    if ast.error:
                        return res.failure(ast.error)
                    str_components[str_components.index(val)] = ast.node

            res.register_advancement()
            self.advance()
            return res.success(StringNode(str_components, tok.pos_start, tok.pos_end))

        elif tok.matches(TT_KEYWORD, 'Verus') or tok.matches(TT_KEYWORD, 'Falsus'):
            res.register_advancement()
            self.advance()
            return res.success(BoolNode(tok))

        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            var_name = tok
            idxes_to_get = []
            attr_to_get = None

            if self.current_tok.type == TT_LSQUARE:
                while self.current_tok.type == TT_LSQUARE:
                    res.register_advancement()
                    self.advance()

                    idxes_to_get.append(res.register(self.bin_op(
                        self.comp_expr, ((TT_KEYWORD, 'et'), (TT_KEYWORD, 'aut')))))

                    if res.error:
                        return res

                    res.register_advancement()
                    self.advance()

            if self.current_tok.type == TT_DOT:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(ExpectedItemError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected Identifier"
                    ))

                attr_to_get = self.current_tok.value
                res.register_advancement()
                self.advance()

            return res.success(VarAccessNode(var_name, idxes_to_get, attr_to_get))

        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(ExpectedItemError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))

        elif tok.type == TT_LSQUARE:
            list_expr = res.register(self.list_expr())
            if res.error:
                return res
            return res.success(list_expr)
        elif tok.type == TT_LBRACE:
            dict_expr = res.register(self.dict_expr())
            if res.error:
                return res
            return res.success(dict_expr)
        elif tok.matches(TT_KEYWORD, 'si'):
            if_expr = res.register(self.if_expr())
            if res.error:
                return res
            return res.success(if_expr)
        elif tok.matches(TT_KEYWORD, 'tempta'):
            try_expr = res.register(self.try_expr())
            if res.error:
                return res
            return res.success(try_expr)
        elif tok.matches(TT_KEYWORD, 'pro'):
            for_expr = res.register(self.for_expr())
            if res.error:
                return res
            return res.success(for_expr)

        elif tok.matches(TT_KEYWORD, 'dum'):
            while_expr = res.register(self.while_expr())
            if res.error:
                return res
            return res.success(while_expr)

        elif tok.matches(TT_KEYWORD, 'opus'):
            func_def = res.register(self.func_def())
            if res.error:
                return res
            return res.success(func_def)

        return res.failure(ExpectedItemError(
            tok.pos_start, tok.pos_end,
            "Expected expression"
        ))

    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != TT_LSQUARE:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '['"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_RSQUARE:
            res.register_advancement()
            self.advance()
        else:
            element_nodes.append(res.register(
                self.expr(could_have_var_assign=False)))
            if res.error:
                return res.failure(ExpectedItemError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ']' or expression"
                ))

            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                element_nodes.append(res.register(self.expr()))
                if res.error:
                    return res

            if self.current_tok.type != TT_RSQUARE:
                return res.failure(ExpectedItemError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected ',' or ']'"
                ))

            res.register_advancement()
            self.advance()

        return res.success(ListNode(
            element_nodes,
            pos_start,
            self.current_tok.pos_end.copy()
        ))

    def dict_expr(self):
        res = ParseResult()
        key_pairs = {}
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != TT_LBRACE:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_RBRACE:
            res.register_advancement()
            self.advance()
        else:
            while True:
                key = res.register(self.expr(could_have_var_assign=False))
                if res.error:
                    return res

                if self.current_tok.type != TT_COLON:
                    return res.failure(ExpectedItemError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ':'"
                    ))

                res.register_advancement()
                self.advance()

                value = res.register(self.expr(could_have_var_assign=False))
                if res.error:
                    return res

                key_pairs[key] = value

                if self.current_tok.type != TT_COMMA:
                    break

                res.register_advancement()
                self.advance()

            res.register_advancement()
            self.advance()

        return res.success(DictNode(key_pairs, pos_start, self.current_tok.pos_end.copy()))

    def if_expr(self):
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases('si'))
        if res.error:
            return res
        cases, else_case = all_cases
        return res.success(IfNode(cases, else_case))

    def if_expr_b(self):
        return self.if_expr_cases('alioquinsi')

    def if_expr_c(self):
        res = ParseResult()
        else_case = None

        if self.current_tok.matches(TT_KEYWORD, 'alioquin'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type == TT_COLON:
                res.register_advancement()
                self.advance()
            else:
                return res.failure(ExpectedItemError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected ':'"
                ))

            if self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

                self.indent_count += 1
                statements = res.register(self.statements())
                self.indent_count -= 1

                if res.error:
                    return res
                else_case = (statements, True)

            else:
                expr = res.register(self.statement())
                if res.error:
                    return res
                else_case = (expr, False)

        return res.success(else_case)

    def if_expr_b_or_c(self):
        res = ParseResult()
        cases, else_case = [], None

        if self.current_tok.matches(TT_KEYWORD, 'alioquinsi'):
            all_cases = res.register(self.if_expr_b())
            if res.error:
                return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.if_expr_c())
            if res.error:
                return res

        return res.success((cases, else_case))

    def if_expr_cases(self, case_keyword):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TT_KEYWORD, case_keyword):
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{case_keyword}'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.type == TT_COLON:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected ':'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_EOF:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected statement", interactive=True
            ))

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            self.indent_count += 1
            statements = res.register(self.statements())
            self.indent_count -= 1

            if res.error:
                return res
            cases.append((condition, statements, True))

            all_cases = res.register(self.if_expr_b_or_c())
            if res.error:
                return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)
        else:
            expr = res.register(self.statement())
            if res.error:
                return res
            cases.append((condition, expr, False))

            all_cases = res.register(self.if_expr_b_or_c())
            if res.error:
                return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return res.success((cases, else_case))

    def try_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'tempta'):
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'tempta'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok == TT_COLON:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected ':'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_EOF:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected statement", interactive=True
            ))

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            self.indent_count += 1
            try_body = res.register(self.statements())
            self.indent_count -= 1
            if res.error:
                return res

            if self.current_tok.matches(TT_KEYWORD, "praeter"):
                self.advance()
                res.register_advancement()

                if self.current_tok.type == TT_IDENTIFIER:
                    except_name = self.current_tok
                    res.register_advancement()
                    self.advance()
                else:
                    except_name = None

                if self.current_tok.matches(TT_KEYWORD, "tam"):
                    res.register_advancement()
                    self.advance()

                    if self.current_tok.type != TT_IDENTIFIER:
                        return res.failure(ExpectedItemError(
                            self.current_tok.pos_start, self.current_tok.pos_end,
                            f"Expected identifier"
                        ))

                    except_as = self.current_tok
                    res.register_advancement()
                    self.advance()
                else:
                    except_as = None

                if self.current_tok == TT_COLON:
                    return res.failure(ExpectedItemError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected ':'"
                    ))

                self.advance()
                res.register_advancement()

                self.indent_count += 1
                except_body = res.register(self.statements())
                self.indent_count -= 1

                if res.error:
                    return res
            else:
                except_body = None
                except_name = None
                except_as = None
        else:
            try_body = res.register(self.expr())
            if res.error:
                return res

            except_body = None
            except_name = None
            except_as = None

        return res.success(TryNode(try_body, except_body, except_name, except_as))

    def for_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'pro'):
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'pro'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected identifier"
            ))

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_EQ:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '='"
            ))

        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TT_KEYWORD, 'ad'):
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'ad'"
            ))

        res.register_advancement()
        self.advance()

        end_value = res.register(self.expr())
        if res.error:
            return res

        if self.current_tok.matches(TT_KEYWORD, 'gradus'):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expr())
            if res.error:
                return res
        else:
            step_value = None

        if not self.current_tok.type == TT_COLON:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected ':'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_EOF:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected statement", interactive=True
            ))

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            self.indent_count += 1
            body = res.register(self.statements())
            self.indent_count -= 1

            if res.error:
                return res

            return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))

        body = res.register(self.statement())
        if res.error:
            return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))

    def while_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'dum'):
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'dum'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.type == TT_COLON:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected ':'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_EOF:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected statement", interactive=True
            ))

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            self.indent_count += 1
            body = res.register(self.statements())
            self.indent_count -= 1

            if res.error:
                return res

            return res.success(WhileNode(condition, body, True))

        body = res.register(self.statement())
        if res.error:
            return res

        return res.success(WhileNode(condition, body, False))

    def func_def(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'opus'):
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'opus'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()
            if self.current_tok.type != TT_LPAREN:
                return res.failure(ExpectedItemError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected '('"
                ))
        else:
            var_name_tok = None
            if self.current_tok.type != TT_LPAREN:
                return res.failure(ExpectedItemError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected identifier or '('"
                ))

        res.register_advancement()
        self.advance()
        arg_name_toks = []

        if self.current_tok.type == TT_IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(ExpectedItemError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected identifier"
                    ))

                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TT_RPAREN:
                return res.failure(ExpectedItemError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected ',' or ')'"
                ))
        else:
            if self.current_tok.type != TT_RPAREN:
                return res.failure(ExpectedItemError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected identifier or ')'"
                ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_ARROW:
            res.register_advancement()
            self.advance()

            body = res.register(self.expr())
            if res.error:
                return res

            return res.success(FuncDefNode(
                var_name_tok,
                arg_name_toks,
                body,
                True
            ))

        if self.current_tok.type != TT_COLON:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '->' or ':'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_EOF:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected statement", interactive=True
            ))

        if self.current_tok.type != TT_NEWLINE:
            return res.failure(ExpectedItemError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected a newline"
            ))

        res.register_advancement()
        self.advance()

        self.indent_count += 1
        body = res.register(self.statements())
        self.indent_count -= 1

        if res.error:
            return res

        res.register_advancement()
        self.advance()

        return res.success(FuncDefNode(
            var_name_tok,
            arg_name_toks,
            body,
            False
        ))

    ###################################

    def bin_op(self, func_a, ops, func_b=None):
        if func_b == None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        if res.error:
            return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)
