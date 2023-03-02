from abc import ABC, abstractmethod
from .tokens import *
from typing import Any


literals = {
    TokenType.TRUE,
    TokenType.FALSE,
    TokenType.NUMBER,
    TokenType.STRING,
    TokenType.CELL_REF,
    TokenType.CELL_RANGE,
}


class Expr(ABC):
    @abstractmethod
    def eval(self, cell_ref_table: dict[str, Any]):
        pass


class BinOp(Expr):
    def __init__(self, op: TokenType, left: Expr, right: Expr) -> None:
        self.op = op
        self.left = left
        self.right = right

    def eval(self, cell_ref_table: dict[str, Any]):
        left = self.left.eval(cell_ref_table=cell_ref_table)
        right = self.right.eval(cell_ref_table=cell_ref_table)

        if self.op == TokenType.ADDITION:
            return left + right
        elif self.op == TokenType.SUBTRACTION:
            return left - right
        elif self.op == TokenType.MULTIPLICATION:
            return left * right
        elif self.op == TokenType.EXPONENT:
            return left**right
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

    def eval(self, cell_ref_table: dict[str, Any]):
        if self.operator.type == TokenType.SUBTRACTION:
            return -self.operand.eval(cell_ref_table=cell_ref_table)
        else:
            return self.operand.eval(cell_ref_table=cell_ref_table)

    def __repr__(self) -> str:
        return f"Unary({self.operator}, {self.operand})"


class Literal(Expr):
    def __init__(self, token: Token) -> None:
        self.token = token

    def resolve_cell_ref(self) -> Any:
        pass

    def resolve_cell_range(self) -> list[Any]:
        pass

    def eval(self, cell_ref_table: dict[str, Any]):
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
            return cell_ref_table[self.token.text]
        elif self.token.type == TokenType.CELL_RANGE:
            return self.resolve_cell_range()
        else:
            return None

    def __repr__(self) -> str:
        return f"Literal({self.token.text})"


def and_impl(*args: list[Expr]):
    for i in range(len(args)):
        if not args[i]:
            return False
    return True


def if_impl(*args: list[Expr]):
    if len(args) > 3:
        raise Exception("Too many args provided to IF function.")
    elif len(args) == 2:
        if args[0]:
            return args[1]
        else:
            return False
    elif len(args) == 3:
        if args[0]:
            return args[1]
        else:
            return args[2]


def not_impl(*args: list[Expr]):
    if not len(args) == 1:
        raise Exception("Too many args provided to NOT function.")
    else:
        arg = args[0]
        if not arg:
            return True
        else:
            return False


library = {"and": and_impl, "if": if_impl, "not": not_impl}


class FunctionCall(Expr):
    def __init__(self, identifier: Token, arguments: list[Expr]) -> None:
        self.identifier = identifier
        self.arguments = arguments

    def eval(self, cell_ref_table: dict[str, Any]):
        func = self.identifier.text.lower()
        if func in library:
            evaluated_args = [
                arg.eval(cell_ref_table=cell_ref_table) for arg in self.arguments
            ]
            return library[func](*evaluated_args)
        else:
            raise Exception(f"Identifier: {self.identifier} not found in library.")

    def __repr__(self) -> str:
        return f"FunctionCall({self.identifier}, {self.arguments})"
