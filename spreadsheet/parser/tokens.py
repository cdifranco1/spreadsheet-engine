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


keywords = {"true": TokenType.TRUE, "false": TokenType.FALSE}


literals = {
    TokenType.TRUE,
    TokenType.FALSE,
    TokenType.NUMBER,
    TokenType.STRING,
    TokenType.CELL_REF,
    TokenType.CELL_RANGE,
}

comparisons = {TokenType.GT, TokenType.GTE, TokenType.LTE, TokenType.LT}


class Token:
    def __init__(self, token_type: TokenType, text: str) -> None:
        self.type = token_type
        self.text = text

    def __str__(self) -> str:
        return f"Token({self.type},{self.text})"
