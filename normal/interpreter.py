DIGITS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]

class Error:
    def __init__(self, error, reason):
        self.error = error
        self.reason = reason
    
    def as_string(self):
        return f"{self.error}: {self.reason}"

    def __repr__(self):
        return f"(ERROR {self.error}: {self.reason})"

class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
    
    def __eq__(self, value):
        if self.value != None and value.value != None:
            if self.type != value.type:
                return False
            
            if self.value != value.value:
                return False
            
            return True
        
        return self.type == value.type

    def __ne__(self, value):
        return not self.__eq__(value)

    def __add__(self, value):
        if self != Token("NUMBER"):
            return None, Error("TypeError", f"Expected number, got {self.type.lower()}")
        
        if value != Token("NUMBER"):
            return None, Error("TypeError", f"Expected number, got {value.type.lower()}")
        
        return Token("NUMBER", self.value + value.value), None
    
    def __sub__(self, value):
        if self != Token("NUMBER"):
            return None, Error("TypeError", f"Expected number, got {self.type.lower()}")
        
        if value != Token("NUMBER"):
            return None, Error("TypeError", f"Expected number, got {value.type.lower()}")
        
        return Token("NUMBER", self.value - value.value), None
    
    def __mul__(self, value):
        if self != Token("NUMBER"):
            return None, Error("TypeError", f"Expected number, got {self.type.lower()}")
        
        if value != Token("NUMBER"):
            return None, Error("TypeError", f"Expected number, got {value.type.lower()}")
        
        return Token("NUMBER", self.value * value.value), None
    
    def __truediv__(self, value):
        if self != Token("NUMBER"):
            return None, Error("TypeError", f"Expected number, got {self.type.lower()}")
        
        if value != Token("NUMBER"):
            return None, Error("TypeError", f"Expected number, got {value.type.lower()}")
        
        if value == Token("NUMBER", 0):
            return None, Error("MathError", f"Cannot divide {self.value} to 0")
        
        return Token("NUMBER", self.value / value.value), None
    
    def __neg__(self):
        if self != Token("NUMBER"):
            return None, Error("TypeError", f"Expected number, got {self.type.lower()}")
        
        return Token("NUMBER", -self.value)

    def __repr__(self):
        return f"(TOKEN {self.type}: VALUE {self.value})" if self.value else f"(TOKEN {self.type})"

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
                            tokens[-1] = Token("PLUS") if element == Token("MINUS") else Token("MINUS")
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
                case "(":
                    tokens += [Token("LPAREN")]
                    self.advance()
                case ")":
                    tokens += [Token("RPAREN")]
                    self.advance()
                case _:
                    if self.current_char in " \n\t":
                        self.advance()
                        continue

                    if self.current_char in DIGITS + ["."]:
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

class ShuntingYard:
    def __init__(self, tokens):
        self.tokens = tokens
    
    def turn_to_postfix(self):
        postfix = []
        operators = []
        precedence = {
            "PLUS": 1,
            "MINUS": 1,
            "MUL": 2,
            "DIV": 2,
            "POW": 3,
            "LPAREN": 0
        }
        for token in self.tokens:
            if token == Token("NUMBER"):
                postfix += [token]
            else:
                match token.type:
                    case "LPAREN":
                        operators += ["LPAREN"]
                    case "RPAREN":
                        if "LPAREN" not in operators:
                            return [], Error("SyntaxError", "Unexpected ')'")

                        while operators[-1] != "LPAREN":
                            postfix += [Token(operators.pop())]
                        
                        operators.pop()
                    case _:
                        if not operators:
                            operators += [token.type]
                            continue

                        if precedence[token.type] <= precedence[operators[-1]]:
                            postfix += [Token(operators.pop())]
                        
                        operators += [token.type]
        
        temp = operators.copy()
        while operators:
            match operators.pop():
                case "LPAREN":
                    return [], Error("SyntaxError", "Unexpected '('")
        
        return postfix + list(map(lambda x: Token(x), temp[::-1])), None

class Interpreter:
    def __init__(self, postfix):
        self.postfix = postfix
    
    def run_postfix(self):
        stack = []
        for token in self.postfix:
            if token == Token("NUMBER"):
                stack += [token]
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

        return stack[0], None

def get_last(array):
    if array:
        return array[-1]
    
    return None

def run(snippet):
    lexer = Lexer(snippet)
    tokens, error = lexer.make_tokens()
    if error:
        print(error.as_string())
        return

    shunting_yard = ShuntingYard(tokens)
    postfix, error = shunting_yard.turn_to_postfix()
    if error:
        print(error.as_string())
        return

    interpreter = Interpreter(postfix)
    if error:
        print(error.as_string())
        return

    res, error = interpreter.run_postfix()
    if error:
        print(error.as_string())
        return
    
    print(res)

file = input("Which file do you want to run? ")
with open(f"{file}.normal") as file:
    lines = file.read().split("\n")

line = 0
while line < len(lines):
    if lines[line].strip():
        run(lines[line])

    line += 1