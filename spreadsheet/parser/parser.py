from abc import ABC


"""
Grammar:

expression     -> ifExpression | notExpression | equality ;

   ** building these control expressions into the language explicitly instead of having separate lookups **

ifExpression   -> "if" "(" equality "," expression "," expression")" ;
notExpression  -> "not" "(" expression ") ;

equality       -> comparison ( "=" comparison )* ;
comparison     -> term ( ( ">" | ">=" | "<" | "<=" ) term )* ;

term           -> factor ( ( "-" | "+" ) factor )* ;
factor         -> unary ( ( "/" | "*" | "^" ) unary )* ;
unary          -> ("-" | "+") unary | function-call ;

*
 When we interpret, we'll need to do a lookup for built-in function calls
*
function-call  -> IDENTIFIER ( "(" arguments? ")" )* ;

primary        -> NUMBER | STRING | IDENTIFIER | "true" | "false" | CELL_REF | CELL_RANGE ;



Utility Rules

arguments      -> expression ( "," expression )* ;

"""

from enum import Enum, auto


class TokenType(Enum):
    OPEN_PAREN = auto()
    CLOSED_PAREN = auto()
    QUOTATION = auto()

    ADDITION = auto()
    SUBTRACTION = auto()
    MULTIPLICATION = auto()
    DIVISION = auto()
    EXPONENT = auto()

    TRUE = auto()
    FALSE = auto()

    # Comparisons
    EQUALS = auto()
    GT = auto()
    LT = auto()
    GTE = auto()
    LTE = auto()

    COLON = auto()

    AND = auto()
    OR = auto()
    IF = auto()
    NOT = auto()

    IDENTIFIER = auto()

    NUMBER = auto()
    CELL_REF = auto()

    EOF = auto()


keywords = {
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "and": TokenType.AND,
    "or": TokenType.OR,
}


from typing import Any


class Token:
    def __init__(self, token_type: TokenType, text: str, literal: Any) -> None:
        self.type = token_type
        self.literal = literal
        self.text = text

    def __str__(self) -> str:
        return f"Token({self.type},{self.text},{self.literal})"


class Scanner:
    start = 0
    current = 0

    tokens = []

    def __init__(self, source: str) -> None:
        self.source = source

    def current_char(self):
        return self.source[self.current]

    def advance(self):
        self.current += 1

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.add_token(TokenType.EOF)
        return self.tokens

    def add_token(self, token_type: TokenType, literal=None):
        text = self.source[self.start : self.current + 1]
        self.tokens.append(Token(token_type=token_type, text=text, literal=literal))
        self.advance()

    def scan_token(self):
        # Number
        if self.current_char().isdigit():
            while self.current_char().isdigit():
                self.advance()
            if self.current_char() == ".":
                while self.current_char().isdigit():
                    self.advance()
            self.add_token(TokenType.NUMBER)

        # Cell Ref
        elif self.current_char().isalpha():
            while self.current_char().isalpha():
                self.advance()
            if self.current_char().isdigit():
                while self.current_char().isdigit():
                    self.advance()
            self.add_token(TokenType.CELL_REF)

        # Groupings
        elif self.current_char() == "(":
            self.add_token(TokenType.OPEN_PAREN)
        elif self.current_char() == ")":
            self.add_token(TokenType.CLOSED_PAREN)
        elif self.current_char() == '"':
            self.advance()
            while self.current_char() != '"':
                self.advance()
            self.add_token(token_type=TokenType.QUOTATION)
        elif self.current_char() == ":":
            self.add_token(token_type=TokenType.COLON)

        # Operators
        elif self.current_char() == "*":
            self.add_token(TokenType.MULTIPLICATION)
        elif self.current_char() == "+":
            self.add_token(TokenType.ADDITION)
        elif self.current_char() == "-":
            self.add_token(TokenType.SUBTRACTION)

        # identifiers
        elif self.current_char().isalpha():
            while not self.is_at_end() and self.current_char().isalpha():
                self.advance()
            token = self.source[self.start : self.current + 1]
            token_type = keywords[token] if token in keywords else TokenType.IDENTIFIER
            self.add_token(token_type=token_type)
        else:
            self.advance()

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def print_tokens(self):
        print([str(token) for token in self.tokens])


# class Expression(ABC):
#     def parse():
#         pass

# class IfExpression:


# class Parser:
#     def parse_expression(input: str) ->
#         if input.startswith("if")


if __name__ == "__main__":
    input_string = "A1 + 2 * (B2 - 3) + SUM(C3:C5)"

    """
    Result should be:
        Expression(BinOp(*, BinOp('+', CellRef(A1), 2)
    """
    # parser = Parser(input_string)
    # result = parser.parse()

    scanner = Scanner(input_string)
    result = scanner.scan_tokens()

    scanner.print_tokens()
