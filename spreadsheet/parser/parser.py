from abc import ABC, abstractmethod
from .tokens import *
from .scanner import *
from .parse_nodes import *
from typing import Any

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
