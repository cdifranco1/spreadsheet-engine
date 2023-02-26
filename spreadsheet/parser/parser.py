from abc import ABC

"""
Grammar:

expression     ->  function-call equality;


equality       -> comparison ( "=" comparison )* ;
comparison     -> term ( ( ">" | ">=" | "<" | "<=" ) term )* ;

term           -> factor ( ( "-" | "+" ) factor )* ;
factor         -> unary ( ( "/" | "*" | "^" ) unary )* ;
unary          -> ("-" | "+") unary | function-call ;

*
 When we interpret, we'll need to do a lookup for built-in function calls
*
function-call  -> IDENTIFIER ("(" arguments ")") expression ;

primary        -> NUMBER | STRING | IDENTIFIER | "true" | "false" | CELL_REF | CELL_RANGE ;



Utility Rules

arguments      -> expression ( "," expression )* ;

"""

from enum import Enum, auto


class TokenType(Enum):
    OPEN_PAREN = auto()
    CLOSED_PAREN = auto()
    QUOTATION = auto()
    COMMA = auto()

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
    CELL_RANGE = auto()
    STRING = auto()

    EOF = auto()


keywords = {
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "and": TokenType.AND,
    "or": TokenType.OR,
}


literals = {
    TokenType.TRUE,
    TokenType.FALSE,
    TokenType.NUMBER,
    TokenType.STRING,
    TokenType.CELL_REF,
    TokenType.CELL_RANGE,
}

comparisons = {TokenType.GT, TokenType.GTE, TokenType.LTE, TokenType.LT}

from typing import Any


class Token:
    def __init__(self, token_type: TokenType, text: str) -> None:
        self.type = token_type
        self.text = text

    def __str__(self) -> str:
        return f"Token({self.type},{self.text})"


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
        elif self.current_char() == '"':
            while self.peek() and self.peek() != '"':
                self.advance()
            self.add_token(token_type=TokenType.QUOTATION)
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


from abc import abstractmethod


class Expr(ABC):
    @abstractmethod
    def eval(self):
        pass


class BinOp(Expr):
    def __init__(self, op: TokenType, left: Expr, right: Expr) -> None:
        self.op = op
        self.left = left
        self.right = right

    def eval(self):
        left = self.left.eval()
        right = self.right.eval()

        if self.op == TokenType.ADDITION:
            return left + right
        elif self.op == TokenType.SUBTRACTION:
            return left - right
        elif self.op == TokenType.MULTIPLICATION:
            return left * right
        elif self.op == TokenType.DIVISION:
            return left / right
        elif self.op == TokenType.SUBTRACTION:
            return left - right
        elif self.op == TokenType.EQUALS:
            return left == right
        elif self.op == TokenType.LT:
            return left < right
        elif self.op == TokenType.LTE:
            return left <= right
        elif self.op == TokenType.GT:
            return left > right
        elif self.op == TokenType.GTE:
            return left >= right

    def __repr__(self) -> str:
        return f"BinOp({self.op},{self.left},{self.right}"


class UnaryOp(Expr):
    def __init__(self, operator: Token, operand: Expr) -> None:
        self.operator = operator
        self.operand = operand

    def eval(self):
        if self.operator.type == TokenType.SUBTRACTION:
            return -self.operand.eval

    def __repr__(self) -> str:
        return f"Unary({self.operator}, {self.operand})"


literals = {
    TokenType.TRUE,
    TokenType.FALSE,
    TokenType.NUMBER,
    TokenType.STRING,
    TokenType.CELL_REF,
    TokenType.CELL_RANGE,
}


class Literal(Expr):
    def __init__(self, token: Token) -> None:
        self.token = token

    def resolve_cell_ref(self) -> Any:
        pass

    def resolve_cell_range(self) -> list[Any]:
        pass

    def eval(self):
        if self.token.type == TokenType.TRUE:
            return True
        elif self.token.type == TokenType.FALSE:
            return False
        # TODO: add a FLOAT token type and eval block
        elif self.token.type == TokenType.NUMBER:
            return int(self.token.text)
        elif self.token.type == TokenType.STRING:
            return self.token.text
        elif self.token.type == TokenType.CELL_REF:
            return self.resolve_cell_ref()
        elif self.token.type == TokenType.CELL_RANGE:
            return self.resolve_cell_range()
        else:
            return None

    def __repr__(self) -> str:
        return f"Literal({self.token.text})"


class FunctionCall(Expr):
    def __init__(self, identifier: Token, arguments: list[Token]) -> None:
        self.identifier = identifier
        self.arguments = arguments

    def __repr__(self) -> str:
        return f"FunctionCall({self.identifier}, {self.arguments})"


class Parser:
    current = 0

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens

    def current_token(self) -> Token:
        return self.tokens[self.current]

    def advance(self):
        self.current += 1

    def previous(self):
        return self.tokens[self.current - 1]

    def match(self, *token_types: TokenType) -> bool:
        if self.current_token().type in token_types:
            self.advance()
            return True
        else:
            return False

    def parse(self) -> Expr:
        return self.equality()

    def equality(self) -> Expr:
        expr = self.comparison()

        while self.match(TokenType.EQUALS):
            right = self.comparison()
            expr = BinOp(op=TokenType.EQUALS, left=expr, right=right)

        return expr

    def comparison(self) -> Expr:
        expr = self.term()

        while self.match(*comparisons):
            op = self.previous()
            right = self.term()
            expr = BinOp(op=op.type, left=expr, right=right)

        return expr

    def term(self) -> Expr:
        """
        term           -> factor ( ( "-" | "+" ) factor )* ;
        """
        expr = self.factor()

        while self.match(TokenType.SUBTRACTION, TokenType.ADDITION):
            op = self.previous()
            right = self.factor()
            expr = BinOp(op=op.type, left=expr, right=right)

        return expr

    def factor(self) -> Expr:
        """
        factor         -> unary ( ( "/" | "*" | "^" ) unary )* ;
        """
        expr = self.unary()

        while self.match(
            TokenType.DIVISION, TokenType.MULTIPLICATION, TokenType.EXPONENT
        ):
            op = self.previous().type
            right = self.unary()
            expr = BinOp(op=op, left=expr, right=right)

        return expr

    def unary(self) -> Expr:
        """
        unary          -> ("-" | "+") unary ;

        List(Token("-", TokenType.Subtraction), Token("if", TokenType.FunctionCall), Token("Token("A1:A5", TokenType.CellRange))
        """
        if self.match(TokenType.SUBTRACTION):
            operator = self.previous()
            operand = self.unary()
            return UnaryOp(operator=operator, operand=operand)

        return self.function_call()

    def function_call(self) -> Expr:
        if self.match(TokenType.IDENTIFIER):
            identifier = self.previous()
            if self.match(TokenType.OPEN_PAREN):
                arguments = self.arguments()
                if self.match(TokenType.CLOSED_PAREN):
                    return FunctionCall(identifier=identifier, arguments=arguments)
                else:
                    raise Exception("Did not find closing parentheses for function")
            else:
                raise Exception("Did not open parentheses for function call")
        else:
            return self.literal()

    def arguments(self) -> Expr:
        args = [self.equality()]
        while self.match(TokenType.COMMA):
            result = self.equality()
            args.append(result)
        return args

    def literal(self) -> Expr:
        if self.match(*literals):
            return Literal(self.previous())
        else:
            raise Exception("No literal found")


if __name__ == "__main__":
    while True:
        _input = input()
        parse_tree = Parser(Scanner(_input).scan_tokens()).parse()
        print(parse_tree)
        result = parse_tree.eval()
        print(result)
