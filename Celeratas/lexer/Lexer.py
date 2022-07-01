#######################################
# IMPORTS
#######################################

from Celeratas.helper.convert_roman import toNum
from Celeratas.helper.errors import InvalidNumeral, IllegalCharError, ExpectedItemError, IndentError
from Celeratas.helper.tokens import *

from .constants import *
from .Position import Position
from .Token import Token

#######################################
# LEXER
#######################################


class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.tab_style = ""
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(
            self.text) else None

    def make_tokens(self):
        tokens = []
        self.start_of_statement = True
        # Start of statements is before character other than space/tab - After this is false, tabs and spaces are ignored by make_spaces() method
        # Grammatical char is set to True is anything other than space/tab is read - This var updates start of statements at the end of while loop
        while self.current_char != None:
            grammatical_char = True
            if self.current_char in ' \t':
                new_toks, error = self.make_space(tokens)
                if error:
                    return [], error
                tokens = new_toks
                grammatical_char = False
            elif self.current_char == '#':
                self.skip_comment()
                self.start_of_statement = True
                grammatical_char = False
            elif self.current_char in ';\n':
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
                self.advance()
                self.start_of_statement = True
                grammatical_char = False
            elif self.current_char in ROMAN_NUMERAL_CHARS:
                token, error = self.make_numeral()
                if error:
                    return [], error
                tokens.append(token)
            elif self.current_char in LETTERS + "_":
                token, error = self.make_identifier()
                if error:
                    return [], error
                tokens.append(token)
            elif self.current_char == ".":
                tokens.append(Token(TT_DOT, pos_start=self.pos))
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '"' or self.current_char == "'":
                # Need the first clause incase the code starts with a quote
                if len(tokens) > 0 and tokens[-1].matches(TT_IDENTIFIER, 'f'):
                    tokens.pop()
                    token, error = self.make_string(fstring=True)
                else:
                    token, error = self.make_string(fstring=False)

                if error:
                    return [], error
                tokens.append(token)
            elif self.current_char == '+':
                tokens.append(self.make_plus())
            elif self.current_char == '-':
                tokens.append(self.make_minus())
            elif self.current_char == '*':
                tokens.append(self.make_mul())
                self.advance()
            elif self.current_char == '/':
                tokens.append(self.make_div())
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(TT_POW, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(TT_LSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(TT_RSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token(TT_LBRACE, pos_start=self.pos))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(TT_RBRACE, pos_start=self.pos))
                self.advance()
            elif self.current_char == '!':
                token, error = self.make_not_equals()
                if error:
                    return [], error
                tokens.append(token)
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
            elif self.current_char == ':':
                tokens.append(Token(TT_COLON, pos_start=self.pos))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

            # When Grammatical Token is read, tabs/spaces from this point on will be ignored
            if self.start_of_statement == True and grammatical_char == True:
                self.start_of_statement = False

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_space(self, tokens):
        pos_start = self.pos.copy()
        if self.start_of_statement:
            if self.current_char == ' ':
                # Check tab style
                if not self.tab_style in ["", "space"]:
                    return [], IndentError(pos_start, self.pos, "Inconsistent indentation")
                # Check if next 3 chars are also space
                for _ in range(3):
                    self.advance()
                    if self.current_char == " ":
                        continue
                    # Throw error if not
                    return None, IndentError(pos_start, self.pos, "Improper indentation")

                self.advance()
                self.tab_style = "space"
                tokens.append(
                    Token(TT_TAB, pos_start=pos_start, pos_end=self.pos))
            elif self.current_char == '\t':
                # Check tab style
                if not self.tab_style in ["", "tab"]:
                    return [], IndentError(pos_start, self.pos, "Inconsistent indentation")

                self.advance()
                self.tab_style = "tab"
                tokens.append(Token(TT_TAB, pos_start=self.pos))
        else:
            self.advance()
        return tokens, None

    def make_numeral(self):
        numeral_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in ROMAN_NUMERAL_CHARS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
            numeral_str += self.current_char
            self.advance()
        # Check if numeral or identifier
        if self.current_char != " ":
            # Return the identifier
            identifier, error = self.make_identifier(numeral_str)
            # Need this extra code because the position of the pos start of the identifier will be behind the pos start of the numeral
            if error:
                return "", error
            return Token(identifier.type, identifier.value, pos_start, identifier.pos_end), None
        # Convert String to Int or Float
        numeral_final = toNum(numeral_str)

        if numeral_final == None:
            return None, InvalidNumeral(pos_start, self.pos, f"{numeral_str} is not a valid numeral")

        return Token(TT_NUMERAL, numeral_final, pos_start, self.pos), None

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

    def make_string(self, fstring):
        pos_start = self.pos.copy()
        escape_character = False
        # Can be either " or '
        string_char = self.current_char
        self.advance()

        escape_characters = {
            'n': '\n',
            't': '\t'
        }

        str_components = []
        cur_str = ""

        if not self.current_char:
            return None, IllegalCharError(pos_start, self.pos, "Unexpected end to string")

        while self.current_char != string_char:
            if escape_character:
                # If the escape character is not in the lookup, it simply adds the character
                string += escape_characters.get(self.current_char,
                                                self.current_char)
                escape_character = False
            elif self.current_char == '\\':
                # This affect the next iteration
                escape_character = True
            elif self.current_char == "\n":
                return None, IllegalCharError(pos_start, self.pos, "Unexpected end to string")
            elif fstring and self.current_char == "{":
                # Append cur_str to str_components and reset cur_str
                if cur_str != "":
                    str_components.append(cur_str)
                    cur_str = ""

                # Put the text between braces into the string to_lex
                to_lex = ""
                self.advance()

                pos_after_brace = self.pos.copy()

                while self.current_char != "}":
                    to_lex += self.current_char
                    self.advance()

                    if self.current_char == None or self.current_char in "{\n":
                        return None, ExpectedItemError(pos_after_brace, self.pos, "Expected '}'")

                # Lex to_lex and return the error if it exists
                lexer = Lexer("fstring", to_lex)
                tokens, error = lexer.make_tokens()
                if error:
                    return None, error

                # Check if there is a string in tokens
                for token in tokens:
                    if token.type == TT_STRING:
                        return None, IllegalCharError(pos_after_brace, self.pos, "Unexpected string")

                # Add the tokens to str_components
                str_components.append(tokens)
            else:
                cur_str += self.current_char

            self.advance()
            if self.current_char == None:
                return None, IllegalCharError(pos_start, self.pos, "Unexpected end to string")

        if cur_str != "":
            str_components.append(cur_str)

        self.advance()
        return Token(TT_STRING, str_components, pos_start, self.pos), None

    def make_identifier(self, start_value=""):
        id_str = start_value
        pos_start = self.pos.copy()

        while self.current_char and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()

        tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos), None

    def make_minus(self):
        tok_type = TT_MINUS
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '>':
            self.advance()
            tok_type = TT_ARROW
        elif self.current_char == '=':
            self.advance()
            tok_type = TT_MIN_EQ

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None

        self.advance()
        return None, ExpectedItemError(pos_start, self.pos, "'=' (after '!')")

    def make_mult_toks(self, tok_type_1, tok_type_2, switch_factor):
        tok_type = tok_type_1
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == switch_factor:
            self.advance()
            tok_type = tok_type_2

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_plus(self):
        return(self.make_mult_toks(TT_PLUS, TT_PLUS_EQ, "="))

    def make_mul(self):
        return(self.make_mult_toks(TT_MUL, TT_MUL_EQ, "="))

    def make_div(self):
        return(self.make_mult_toks(TT_DIV, TT_DIV_EQ, "="))

    def make_equals(self):
        return self.make_mult_toks(TT_EQ, TT_EE, "=")

    def make_less_than(self):
        return self.make_mult_toks(TT_LT, TT_LTE, "=")

    def make_greater_than(self):
        return self.make_mult_toks(TT_GT, TT_GTE, "=")

    def skip_comment(self):
        self.advance()

        # Exclusive incase it reachs the EOF and self.current_char == None
        while self.current_char and self.current_char not in ';\n':
            self.advance()

        self.advance()
