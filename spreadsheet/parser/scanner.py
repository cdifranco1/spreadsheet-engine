from .tokens import *


class Scanner:
    def __init__(self, source: str) -> None:
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0

    def current_char(self):
        return self.source[self.current]

    def advance(self):
        self.current += 1

    def peek(self):
        if self.current < len(self.source) - 1:
            return self.source[self.current + 1]
        return None

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.start = self.current
        self.add_token(TokenType.EOF)
        return self.tokens

    def add_token(self, token_type: TokenType, literal=None):
        if literal:
            self.tokens.append(Token(token_type=token_type, text=literal))
        else:
            text = self.source[self.start : self.current + 1]
            self.tokens.append(Token(token_type=token_type, text=text))

        self.advance()

    def scan_token(self):
        # Number
        if self.current_char().isdigit():
            while self.peek() and self.peek().isdigit():
                self.advance()

            if self.current_char() == ".":
                while self.peek() and self.peek().isdigit():
                    self.advance()

            self.add_token(TokenType.NUMBER)

        # Comparisons
        elif self.current_char() == "=":
            self.add_token(TokenType.EQUALS)
        elif self.current_char() == ">":
            if self.peek() == "=":
                self.advance()
                self.add_token(TokenType.GTE)
            else:
                self.add_token(TokenType.GT)
        elif self.current_char() == "<":
            if self.peek() == "=":
                self.advance()
                self.add_token(TokenType.LTE)
            else:
                self.add_token(TokenType.LT)

        # Groupings
        elif self.current_char() == "(":
            self.add_token(TokenType.OPEN_PAREN)
        elif self.current_char() == ")":
            self.add_token(TokenType.CLOSED_PAREN)
        elif self.current_char() == '"' or self.current_char() == "'":
            while self.peek() and not (self.peek() == '"' or self.peek() == "'"):
                self.advance()
            self.advance()
            self.add_token(token_type=TokenType.STRING)
        elif self.current_char() == ":":
            self.add_token(token_type=TokenType.COLON)

        # Operators
        elif self.current_char() == "*":
            self.add_token(TokenType.MULTIPLICATION)
        elif self.current_char() == "/":
            self.add_token(TokenType.DIVISION)
        elif self.current_char() == "+":
            self.add_token(TokenType.ADDITION)
        elif self.current_char() == "-":
            self.add_token(TokenType.SUBTRACTION)
        elif self.current_char() == "^":
            self.add_token(TokenType.EXPONENT)
        elif self.current_char() == ",":
            self.add_token(TokenType.COMMA)

        # Cell Refs and Identifiers
        elif self.current_char().isalpha():
            while self.peek() and self.peek().isalpha():
                self.advance()

            if self.peek() and self.peek().isdigit():
                while self.peek() and self.peek().isdigit():
                    self.advance()

                if (
                    len(self.tokens) >= 2
                    and self.tokens[-1].type == TokenType.COLON
                    and self.tokens[-2].type == TokenType.CELL_REF
                ):
                    self.tokens.pop()
                    start_ref = self.tokens.pop().text
                    end_ref = self.source[self.start : self.current + 1]
                    self.add_token(
                        TokenType.CELL_RANGE, literal=f"{start_ref}:{end_ref}"
                    )
                else:
                    self.add_token(TokenType.CELL_REF)

            else:
                token = self.source[self.start : self.current + 1].lower()
                token_type = (
                    keywords[token] if token in keywords else TokenType.IDENTIFIER
                )
                self.add_token(token_type=token_type)
        else:
            self.advance()

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def print_tokens(self):
        print([str(token) for token in self.tokens])
