from string import ascii_letters

DIGITS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
LETTERS = list(ascii_letters)
KEYWORDS = [
    "variable",
    "is",
    "let",
    "now",
    "be",
    "constant",
    "and",
    "or",
    "not",
    "if",
    "else"
]

OFFICIAL_DATA_TYPES = [
    "NUMBER",
    "BOOLEAN"
]

NONE_VALUES_DICT = {
    "PLUS": "+",
    "MINUS": "-",
    "MUL": "*",
    "DIV": "/",
    "POW": "^",
    "LPAREN": "(",
    "RPAREN": ")",
    "EE": "=",
    "NE": "!",
    "GT": ">",
    "LT": "<",
    "GE": ">",
    "LE": "<",
    "COLON": ":"
}

# Errors
class Error:
    def __init__(self, error, reason):
        self.error = error
        self.reason = reason
    
    def as_string(self):
        return f"{self.error}: {self.reason}"

    def __repr__(self):
        return f"(ERROR {self.error}: {self.reason})"

# Basic components
class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
    
    def __eq__(self, value):
        if not isinstance(value, Token):
            return translate_boolean(False)
        
        if self.type != value.type:
            return translate_boolean(False)

        if self.value != None and value.value != None:
            if self.value != value.value:
                return translate_boolean(False)
            
            return translate_boolean(True)
        
        if value.value == None:
            return translate_boolean(True)
        
        return translate_boolean(self.value == value.value)

    def __ne__(self, value):
        return translate_boolean(not translate_boolean(self.__eq__(value)))
    
    def __gt__(self, value):
        if not isinstance(value, Token):
            return translate_boolean(False), None
        
        if self.type not in ["NUMBER", "BOOLEAN"]:
            return None, Error("TypeError", f"Expected number, got {self.type.lower()}")
        
        if value.type not in ["NUMBER", "BOOLEAN"]:
            return None, Error("TypeError", f"Expected number, got {self.type.lower()}")
        
        if self.type == "BOOLEAN":
            a = translate_boolean(self)
        else:
            a = self.value
        
        if value.type == "BOOLEAN":
            b = translate_boolean(value)
        else:
            b = value.value

        return translate_boolean(float(a) > float(b)), None
    
    def __ge__(self, value):
        res, error = self.__gt__(value)
        if error:
            return None, error
        
        return translate_boolean(translate_boolean(res) or translate_boolean(self.__eq__(value))), None
    
    def __lt__(self, value):
        if not isinstance(value, Token):
            return translate_boolean(False), None
        
        if self.type not in ["NUMBER", "BOOLEAN"]:
            return None, Error("TypeError", f"Expected number, got {self.type.lower()}")
        
        if value.type not in ["NUMBER", "BOOLEAN"]:
            return None, Error("TypeError", f"Expected number, got {self.type.lower()}")
        
        if self.type == "BOOLEAN":
            a = translate_boolean(self)
        else:
            a = self.value

        if value.type == "BOOLEAN":
            b = translate_boolean(value)
        else:
            b = value.value

        return translate_boolean(float(a) < float(b)), None
    
    def __le__(self, value):
        res, error = self.__lt__(value)
        if error:
            return None, error
        
        return translate_boolean(translate_boolean(res) or translate_boolean(self.__eq__(value))), None

    def __add__(self, value):
        if self.type not in ["NUMBER", "BOOLEAN"]:
            return None, Error("TypeError", f"Expected number, got {self.type.lower()}")
        
        if value.type not in ["NUMBER", "BOOLEAN"]:
            return None, Error("TypeError", f"Expected number, got {value.type.lower()}")
        
        res = float(self.value) + float(value.value)
        return Token("NUMBER", int(res) if res % 1 == 0 else res), None
    
    def __sub__(self, value):
        if self.type not in ["NUMBER", "BOOLEAN"]:
            return None, Error("TypeError", f"Expected number, got {self.type.lower()}")
        
        if value.type not in ["NUMBER", "BOOLEAN"]:
            return None, Error("TypeError", f"Expected number, got {value.type.lower()}")
        
        res = float(self.value) - float(value.value)
        print("SUBTRACTION", res)
        return Token("NUMBER", int(res) if res % 1 == 0 else res), None
    
    def __mul__(self, value):
        if self not in ["NUMBER", "BOOLEAN"]:
            return None, Error("TypeError", f"Expected number, got {self.type.lower()}")
        
        if value not in ["NUMBER", "BOOLEAN"]:
            return None, Error("TypeError", f"Expected number, got {value.type.lower()}")
        
        res = float(self.value) * float(value.value)
        return Token("NUMBER", int(res) if res % 1 == 0 else res), None
    
    def __truediv__(self, value):
        if self not in ["NUMBER", "BOOLEAN"]:
            return None, Error("TypeError", f"Expected number, got {self.type.lower()}")
        
        if value not in ["NUMBER", "BOOLEAN"]:
            return None, Error("TypeError", f"Expected number, got {value.type.lower()}")
        
        if check(value, Token("NUMBER", 0)):
            return None, Error("MathError", f"Cannot divide {self.value} to 0")
        
        res = float(self.value) / float(value.value)
        return Token("NUMBER", int(res) if res % 1 == 0 else res), None
    
    def __pow__(self, value):
        if self not in ["NUMBER", "BOOLEAN"]:
            return None, Error("TypeError", f"Expected number, got {self.type.lower()}")
        
        if value not in ["NUMBER", "BOOLEAN"]:
            return None, Error("TypeError", f"Expected number, got {value.type.lower()}")
        
        res = float(self.value) ** float(value.value)
        return Token("NUMBER", int(res) if res % 1 == 0 else res), None
    
    def __neg__(self):
        if self not in ["NUMBER", "BOOLEAN"]:
            return None, Error("TypeError", f"Expected number, got {self.type.lower()}")
        
        return Token("NUMBER", -self.value)

    def __repr__(self):
        return f"(TOKEN {self.type}: {self.value})" if self.value else f"(TOKEN {self.type})"

class Variable:
    def __init__(self, name, value, immutable):
        self.name = name
        self.value = value
        self.immutable = immutable
    
    def __repr__(self):
        return f"(VARIABLE {self.name}: {self.value.__repr__()})"

class SymbolTable:
    def __init__(self):
        self.table = {}

    def update(self, var_object):
        if var_object.name in self.table:
            if self.table[var_object.name].immutable:
                return None, Error("VariableError", f"Variable '{var_object.name}' cannot be changed")
        
        self.table.update({var_object.name: var_object})
        return var_object.value, None
    
    def get(self, name):
        if name not in self.table:
            return None, Error("VariableError", f"Variable '{name}' is not defined")
        
        return self.table[name].value, None
    
    def __repr__(self):
        current = "(SYMBOL TABLE: "
        for key in self.table:
            current += f"({key}: {self.table[key].value.__repr__()}), "

        current = current[0:len(current)-2]
        current += ")"
        return current

symbol_table = SymbolTable()

# Lexer
class Lexer:
    def __init__(self, text):
        self.text = text
        self.index = -1
        self.current_char = None
        self.advance()
    
    def advance(self):
        self.index += 1
        self.current_char = None if self.index >= len(self.text) else self.text[self.index]
    
    def make_tokens(self):
        tokens = []
        while self.current_char:
            match self.current_char:
                case "+":
                    element = get_last(tokens)
                    if element:
                        if element.type in ["PLUS", "MINUS"]:
                            self.advance()
                            continue
                    
                    tokens += [Token("PLUS")]
                    self.advance()
                case "-":
                    element = get_last(tokens)
                    if element:
                        if element.type in ["PLUS", "MINUS"]:
                            tokens[-1] = Token("PLUS") if check(element, Token("MINUS")) else Token("MINUS")
                            self.advance()
                            continue

                    tokens += [Token("MINUS")]
                    self.advance()
                case "*":
                    tokens += [Token("MUL")]
                    self.advance()
                case "/":
                    tokens += [Token("DIV")]
                    self.advance()
                case "^":
                    tokens += [Token("POW")]
                    self.advance()
                case "=":
                    res, error = self.make_ee()
                    if error:
                        return None, error
                    
                    tokens += [res]
                    self.advance()
                case "!":
                    res, error = self.make_ne()
                    if error:
                        return None, error
                    
                    tokens += [res]
                    self.advance()
                case ">":
                    res, error = self.make_greater_or_equal()
                    if error:
                        return None, error
                    
                    tokens += [res]
                    self.advance()
                case "<":
                    res, error = self.make_smaller_or_equal()
                    if error:
                        return None, error
                    
                    tokens += [res]
                    self.advance()
                case "(":
                    tokens += [Token("LPAREN")]
                    self.advance()
                case ")":
                    tokens += [Token("RPAREN")]
                    self.advance()
                case ":":
                    tokens += [Token("COLON")]
                    self.advance()
                case _:
                    if self.current_char in " \n\t":
                        self.advance()
                        continue

                    if self.current_char in LETTERS + ["_"]:
                        token, error = self.make_identifier_or_keyword()
                        if error:
                            return [], error
                        
                        tokens += [token]
                    elif self.current_char in DIGITS + ["."]:
                        token, error = self.make_numbers()
                        if error:
                            return [], error

                        tokens += [token]
                    else:
                        return [], Error("SyntaxError", f"Unexpected character: '{self.current_char}'")
        
        return tokens, None
    
    def make_numbers(self):
        number = ""
        while self.current_char in DIGITS + ["."]:
            number += self.current_char
            self.advance()
        
        if "." not in number:
            return Token("NUMBER", int(number)), None
        
        if number.count(".") > 1:
            return None, Error("SyntaxError", f"Expect only one '.' in a number, got {number.count(".")}/1")
        
        return Token("NUMBER", float(number)), None
    
    def make_identifier_or_keyword(self):
        global LETTERS, DIGITS
        identifier = ""
        while self.current_char in LETTERS + DIGITS + ["_"]:
            identifier += self.current_char
            self.advance()
        
        if identifier in KEYWORDS:
            return Token("KEYWORD", identifier), None
        
        if identifier in ["true", "false"]:
            return Token("BOOLEAN", identifier), None
        
        return Token("IDENTIFIER", identifier), None
    
    def make_ee(self):
        self.advance()
        if self.current_char != "=":
            if self.current_char:
                return None, Error("SyntaxError", f"Expected '=', not '{self.current_char}'")
            
            return None, Error("SyntaxError", "Expected '='")
        
        return Token("EE"), None

    def make_ne(self):
        self.advance()
        if self.current_char != "=":
            if self.current_char:
                return None, Error("SyntaxError", f"Expected '=', not '{self.current_char}'")
            
            return None, Error("SyntaxError", "Expected '='")
        
        return Token("NE"), None
    
    def make_greater_or_equal(self):
        self.advance()
        if self.current_char == "=":
            return Token("GE"), None
        
        return Token("GT"), None
    
    def make_smaller_or_equal(self):
        self.advance()
        if self.current_char == "=":
            return Token("SE"), None
        
        return Token("ST"), None

# Parser
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = -1
        self.current_token = None
        self.advance()
    
    def advance(self):
        self.index += 1
        self.current_token = self.tokens[self.index] if 0 <= self.index < len(self.tokens) else None
    
    def move_back(self):
        self.index -= 1
        self.current_token = self.tokens[self.index] if 0 <= self.index < len(self.tokens) else None
    
    def generate_syntax_branch(self):
        if not self.tokens:
            return None, None, Error("SyntaxError", "No value to parse")

        if (self.current_token.type, self.current_token.value) in [("KEYWORD", "variable"), ("KEYWORD", "let")]:
            res, error = self.variable_declaration()
            if error:
                return "var", None, error
            
            return "var", res, None

        if check(self.current_token, Token("KEYWORD", "constant")):
            res, error = self.const_variable_declaration()
            if error:
                return "const", None, error
            
            return "const", res, None
        
        if check(self.current_token, Token("KEYWORD", "else")):
            self.advance()
            if check(self.current_token, Token("KEYWORD", "if")):
                return None, None, Error("else if has no parent if")
            
            return None, None, Error("else has no parent if")
        
        if check(self.current_token, Token("KEYWORD", "if")):
            res, error = self.if_statement()
            if error:
                return "if", None, error
            
            return "if", res, None

        if check(self.current_token, Token("IDENTIFIER")):
            self.advance()
            if check(self.current_token, Token("KEYWORD")):
                res, error = self.update_variable()
                if error:
                    return "var_update", None, error
                
                return "var_update", res, None

            self.move_back()

        res, error = self.turn_to_postfix()
        if error:
            return "postfix", None, error
        
        return "postfix", res, None

    def turn_to_postfix(self):
        postfix = []
        operators = []
        precedence = {
            "LPAREN": 0,
            "OR": 1,
            "AND": 2,
            "NOT": 3,
            "EE": 4,
            "NE": 4,
            "GT": 4,
            "GE": 4,
            "SE": 4,
            "ST": 4,
            "PLUS": 5,
            "MINUS": 5,
            "MUL": 6,
            "DIV": 6,
            "POW": 7
        }

        while not check(self.current_token, None):
            if self.current_token.type in ["NUMBER", "IDENTIFIER", "BOOLEAN"]:
                postfix += [self.current_token]
            elif check(self.current_token, Token("KEYWORD", "if")):
                stack = []
                if_tok = []
                while not check(self.current_token, None):
                    if check(self.current_token, Token("LPAREN")):
                        stack += [Token("LPAREN")]
                    
                    if check(self.current_token, Token("RPAREN")):
                        if not stack:
                            break

                        if not check(stack.pop(), Token("LPAREN")):
                            return None, Error("SyntaxError", "Unexpected ')'")
                    
                    if_tok += [self.current_token]
                    self.advance()
                
                if check(self.current_token, Token("RPAREN")):
                    if "LPAREN" not in operators:
                        return None, Error("SyntaxError", "Unexpected ')'")

                    operators = operators[::-1]
                    operators.remove("LPAREN")
                    operators = operators[::-1]
                
                new_parser = Parser(if_tok)
                type_, res, error = new_parser.generate_syntax_branch()
                if error:
                    return None, error
                
                new_interpreter = Interpreter(type_, res)
                res, error = new_interpreter.run_tokens()
                if error:
                    return None, error
                
                postfix += [res]
            elif check(self.current_token, Token("KEYWORD")):
                return None, Error("SyntaxError", f"'{NONE_VALUES_DICT.get(self.current_token.type, self.current_token.value)}' can't be in expressions")
            else:
                match self.current_token.type:
                    case "LPAREN":
                        operators += ["LPAREN"]
                    case "RPAREN":
                        if "LPAREN" not in operators:
                            return None, Error("SyntaxError", "Unexpected ')'")

                        while operators[-1] != "LPAREN":
                            postfix += [Token(operators.pop())]
                        
                        operators.pop()
                    case _:
                        if not operators:
                            operators += [self.current_token.type]
                            self.advance()
                            continue

                        if self.current_token.type not in precedence:
                            return None, Error("SyntaxError", f"Unexpected character: '{NONE_VALUES_DICT[self.current_token.type]}'")

                        if precedence[self.current_token.type] <= precedence[operators[-1]] and precedence[self.current_token.type] != precedence["POW"] and precedence[operators[-1]] != precedence["POW"]:
                            postfix += [Token(operators.pop())]
                        
                        operators += [self.current_token.type]
            
            self.advance()
        
        temp = operators.copy()
        while operators:
            match operators.pop():
                case "LPAREN":
                    return None, Error("SyntaxError", "Unexpected '('")

        return postfix + list(map(lambda x: Token(x), temp[::-1])), None
    
    def variable_declaration(self):
        keyword = self.current_token
        self.advance()
        if not self.current_token:
            return None, Error("SyntaxError", "Expected identifier")
        
        if not check(self.current_token, Token("IDENTIFIER")):
            return None, Error("SyntaxError", f"Expected identifier, got '{NONE_VALUES_DICT.get(self.current_token.type, self.current_token.value)}'")
        
        variable_name = self.current_token.value
        self.advance()
        if check(keyword, Token("KEYWORD", "variable")):
            if not self.current_token:
                return None, Error("SyntaxError", "Expected 'is'")
            
            if not check(self.current_token, Token("KEYWORD", "is")):
                return None, Error("SyntaxError", f"Expected 'is', got '{NONE_VALUES_DICT.get(self.current_token.type, self.current_token.value)}'")
        elif not self.current_token:
            return None, Error("SyntaxError", "Expected 'be'")
        elif not check(self.current_token, Token("KEYWORD", "be")):
            return None, Error("TypeError", f"Expected 'be', got '{NONE_VALUES_DICT.get(self.current_token.type, self.current_token.value)}'")
        
        self.advance()
        new_tokens = self.tokens[self.index:]
        new_parser = Parser(new_tokens)
        type_, value, error = new_parser.generate_syntax_branch()
        if error:
            return None, error
        
        new_interpreter = Interpreter(type_, value)
        value, error = new_interpreter.run_tokens()
        if error:
            return None, error
        
        if variable_name in symbol_table.table:
            return None, Error("SyntaxError", f"There is already a declaration with the name '{variable_name}'")

        return Variable(variable_name, value, False), None
    
    def const_variable_declaration(self):
        self.advance()
        if not self.current_token:
            return None, Error("SyntaxError", "Expected identifier")
        
        if not check(self.current_token, Token("IDENTIFIER")):
            return None, Error("SyntaxError", f"Expected identifier, got '{NONE_VALUES_DICT.get(self.current_token.type, self.current_token.value)}'")
        
        variable_name = self.current_token.value
        self.advance()
        if not self.current_token:
            return None, Error("Expected 'is'")
        
        if not check(self.current_token, Token("KEYWORD", "is")):
            return None, Error("SyntaxError", f"Expected 'is', got '{NONE_VALUES_DICT.get(self.current_token.type, self.current_token.value)}'")
        
        self.advance()
        new_tokens = self.tokens[self.index:]
        new_parser = Parser(new_tokens)
        type_, value, error = new_parser.generate_syntax_branch()
        if error:
            return None, error
        
        new_interpreter = Interpreter(type_, value)
        value, error = new_interpreter.run_tokens()
        if error:
            return None, error
        
        return Variable(variable_name, value, True), None
    
    def update_variable(self):
        self.move_back()
        variable_name = self.current_token.value

        self.advance()
        if not check(self.current_token, Token("KEYWORD", "is")):
            return None, Error("SyntaxError", f"Expected 'is', got '{NONE_VALUES_DICT.get(self.current_token.type, self.current_token.value)}'")
        
        self.advance()
        if not check(self.current_token, Token("KEYWORD", "now")):
            return None, Error("SyntaxError", f"Expected 'now', got '{NONE_VALUES_DICT.get(self.current_token.type, self.current_token.value)}'")
        
        self.advance()
        new_tokens = self.tokens[self.index:]
        new_parser = Parser(new_tokens)

        type_, value, error = new_parser.generate_syntax_branch()
        if error:
            return None, error
        
        new_interpreter = Interpreter(type_, value)
        value, error = new_interpreter.run_tokens()
        if error:
            return None, error

        if variable_name not in symbol_table.table:
            return None, Error("SyntaxError", f"There are not any variable declaration with the name '{variable_name}'")

        return Variable(variable_name, value, True), None
    
    def if_statement(self, original=[]):
        self.advance()
        
        # check for condition
        condition_tok = []
        stack = []
        while (not check(self.current_token, Token("COLON")) or stack) and not check(self.current_token, None):
            if check(self.current_token, Token("LPAREN")):
                stack += ["LPAREN"]
            elif check(self.current_token, Token("RPAREN")):
                if not stack:
                    return None, Error("SyntaxError", "Unexpected ')'")
                
                if stack.pop() != "LPAREN":
                    return None, Error("SyntaxError", "Unexpected ')'")
                
            condition_tok += [self.current_token]
            self.advance()
        
        if not condition_tok:
            return None, Error("SyntaxError", "Expected condition")

        if not self.current_token:
            return None, Error("SyntaxError", "Expected ':'")
        
        new_parser = Parser(condition_tok)
        ctype, condition, error = new_parser.generate_syntax_branch()
        if error:
            return None, error

        # check for value
        self.advance()
        value_tok = []
        stack = []
        while (not check(self.current_token, Token("KEYWORD", "else")) or stack) and not check(self.current_token, None):
            if check(self.current_token, Token("LPAREN")):
                stack += ["LPAREN"]
            elif check(self.current_token, Token("RPAREN")):
                if not stack:
                    return None, Error("SyntaxError", "Unexpected ')'")
                
                if stack.pop() != "LPAREN":
                    return None, Error("SyntaxError", "Unexpected ')'")
                
            value_tok += [self.current_token]
            self.advance()
        
        if not value_tok:
            return None, Error("SyntaxError", "Expected value")
        
        new_parser = Parser(value_tok)
        vtype, value, error = new_parser.generate_syntax_branch()
        if error:
            return None, error

        if not self.current_token:
            return original + [[(ctype, condition), (vtype, value)]], None
        
        self.advance()
        if check(self.current_token, None):
            return None, Error("SyntaxError", "Expected 'if' or ':'")
        
        if not check(self.current_token, Token("KEYWORD", "if")) and not check(self.current_token, Token("COLON")):
            return None, Error("SyntaxError", f"Expected 'if' or ':', not '{NONE_VALUES_DICT.get(self.current_token, self.current_token.value)}'")
        
        if check(self.current_token, Token("KEYWORD", "if")):
            res, error = self.if_statement(original + [[(ctype, condition), (vtype, value)]])
            if error:
                return None, error
            
            return res, None
        
        self.advance()
        value_tok = self.tokens[self.index:]
        if not value_tok:
            return None, Error("SyntaxError", "Expected value")
        
        new_parser = Parser(value_tok)
        type_, res, error = new_parser.generate_syntax_branch()
        if error:
            return None, error
        
        return original + [[(ctype, condition), (vtype, value)]] + [(type_, res)], None

# Interpreter
class Interpreter:
    def __init__(self, type_, res):
        self.type = type_
        self.res = res
    
    def run_tokens(self):
        match self.type:
            case "var":
                res, error = self.run_variable_declaration()
                if error:
                    return None, error
                
                return res, None
            case "const":
                res, error = self.run_variable_declaration()
                if error:
                    return None, error
                
                return res, None
            case "var_update":
                res, error = self.run_variable_declaration()
                if error:
                    return None, error
                
                return res, None
            case "if":
                res, error = self.run_if()
                if error:
                    return None, error
                
                return res, None
            case "postfix":
                res, error = self.run_postfix()
                if error:
                    return None, error
                
                return res, None

    def run_postfix(self):
        stack = []
        for token in self.res:
            if check(token, Token("NUMBER")) or check(token, Token("BOOLEAN")):
                stack += [token]
            elif check(token, Token("IDENTIFIER")):
                res, error = symbol_table.get(token.value)
                if error:
                    return None, error
                
                stack += [res]
            else:
                match token.type:
                    case "PLUS":
                        if not stack:
                            return None, Error("SyntaxError", "Too less numbers to perform addition, got 0/2")
                        
                        if len(stack) == 1:
                            continue

                        res, error = stack.pop() + stack.pop()
                        if error:
                            return None, error
                        
                        stack += [res]
                    case "MINUS":
                        if not stack:
                            return None, Error("SyntaxError", "Too few numbers to perform subtraction, got 0/2")
                        
                        if len(stack) == 1:
                            res, error = Token("NUMBER", 0) - stack.pop()
                            if error:
                                return None, error
                            
                            stack += [res]
                            continue

                        res, error = -stack.pop() + stack.pop()
                        if error:
                            return None, error
                        
                        stack += [res]
                    case "MUL":
                        operands = len(stack)
                        if operands < 2:
                            return None, Error("SyntaxError", f"Too few numbers to perform subtraction, got {operands}/2")
                        
                        res, error = stack.pop() * stack.pop()
                        if error:
                            return None, error
                        
                        stack += [res]
                    case "DIV":
                        operands = len(stack)
                        if operands < 2:
                            return None, Error("SyntaxError", f"Too few numbers to perform division, got {operands}/2")
                        
                        b = stack.pop()
                        a = stack.pop()
                        res, error = a / b
                        if error:
                            return None, error

                        stack += [res]
                    case "POW":
                        operands = len(stack)
                        if operands < 2:
                            return None, Error("SyntaxError", f"Too few numbers to perform exponentation, got {operands}/2")
                        
                        b = stack.pop()
                        a = stack.pop()
                        res, error = a ** b
                        if error:
                            return None, error
                        
                        stack += [res]
                    case "EE":
                        operands = len(stack)
                        if operands < 2:
                            return None, Error("SyntaxError", f"Too few numbers to perform equality, got {operands}/2")
                        
                        stack += [stack.pop() == stack.pop()]
                    case "NE":
                        operands = len(stack)
                        if operands < 2:
                            return None, Error("SyntaxError", f"Too few numbers to perform inequality, got {operands}/2")
                        
                        stack += [stack.pop() != stack.pop()]
                    case "GT":
                        operands = len(stack)
                        if operands < 2:
                            return None, Error("SyntaxError", f"Too few numbers to perform greater than, got {operands}/2")
                        
                        res, error = stack.pop() < stack.pop()
                        if error:
                            return None, error
                        
                        stack += [res]
                    case "GE":
                        operands = len(stack)
                        if operands < 2:
                            return None, Error("SyntaxError", f"Too few numbers to perform greater than, got {operands}/2")
                        
                        res, error = stack.pop() <= stack.pop()
                        if error:
                            return None, error
                        
                        stack += [res]
                    case "ST":
                        operands = len(stack)
                        if operands < 2:
                            return None, Error("SyntaxError", f"Too few numbers to perform greater than, got {operands}/2")
                        
                        res, error = stack.pop() > stack.pop()
                        if error:
                            return None, error
                        
                        stack += [res]
                    case "SE":
                        operands = len(stack)
                        if operands < 2:
                            return None, Error("SyntaxError", f"Too few numbers to perform greater than, got {operands}/2")
                        
                        res, error = stack.pop() >= stack.pop()
                        if error:
                            return None, error
                        
                        stack += [res]

        return stack[0], None
    
    def run_variable_declaration(self):
        res, error = symbol_table.update(self.res)
        if error:
            return None, error

        return res, None
    
    def run_if(self):
        for pair in self.res:
            if isinstance(pair, list):
                condition_branch = pair[0]
                value_branch = pair[1]
                
                new_interpreter = Interpreter(condition_branch[0], condition_branch[1])
                condition, error = new_interpreter.run_tokens()
                if error:
                    return None, error

                new_interpreter = Interpreter(value_branch[0], value_branch[1])
                value, error = new_interpreter.run_tokens()
                if error:
                    return None, error
                
                if translate_boolean(condition):
                    return value, None

                continue

            new_interpreter = Interpreter(pair[0], pair[1])
            value, error = new_interpreter.run_tokens()
            if error:
                return None, error
            
            return value, None
        
        return None, None

def get_last(array):
    if array:
        return array[-1]
    
    return None

def translate_boolean(value):
    match value:
        case True:
            return Token("BOOLEAN", "true")
        case False:
            return Token("BOOLEAN", "false")
        case _:
            if (value == Token("BOOLEAN", "true")).value == "true":
                return True
            
            if (value == Token("BOOLEAN", "false")).value == "true":
                return False
        
            if value == Token("NUMBER"):
                return value.value != 0

def check(a, b):
    if isinstance(a, Token) or isinstance(b, Token):
        return translate_boolean(a == b)
    
    return a == b

def run(snippet):
    lexer = Lexer(snippet)
    tokens, error = lexer.make_tokens()
    if error:
        print(error.as_string())
        return

    parser = Parser(tokens)
    type_, res, error = parser.generate_syntax_branch()
    if error:
        print(error.as_string())
        return

    interpreter = Interpreter(type_, res)
    res, error = interpreter.run_tokens()
    if error:
        print(error.as_string())
        return

    if res:
        print(res.value)

file = input("Which file do you want to run? ")
with open(f"{file}.normal") as file:
    lines = file.read().split("\n")

line = 0
while line < len(lines):
    if lines[line].strip():
        run(lines[line])

    line += 1
