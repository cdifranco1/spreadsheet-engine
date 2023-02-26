from typing import Any
from parser.parser import Scanner, Parser
import re
import graphlib


class Cell:
    def __init__(self, column_index: str, row_index: str, value=None, formula=None):
        self.column_index = column_index
        self.row_index = row_index
        self.value = value

        self.formula = formula
        self.dependencies = self.get_fomula_deps()

    def get_fomula_deps(self):
        return (
            [col + row for col, row in self.extract_formula_deps()]
            if self.formula
            else []
        )

    def calculate(self, cells: list["Row"]):
        if self.value is not None:
            return self.value
        if self.formula is not None:
            return self.eval_formula(cells)
        return None

    def update_formula(self, new_formula: str) -> None:
        self.formula = new_formula
        self.dependencies = self.get_fomula_deps()

    def eval_formula(self, worksheet: "Sheet") -> None:
        tokens = Scanner(self.formula)
        parse_tree = Parser(tokens).parse()

        dependency_graph = self.build_dependency_graph(worksheet)
        parse_tree.eval(dependency_graph=dependency_graph)

    def extract_formula_deps(self) -> list[str]:
        regex = re.compile("([A-Za-z]+)(\d+)")
        result = regex.findall(self.formula)
        return result

    def has_dependencies(self) -> bool:
        return len(self.dependencies) > 0


class Row:
    def __init__(self, row_index: int, cells=None):
        self.row_index = row_index
        self.cells: list[Cell] = cells or []

    def add_cell(self, cell: Cell):
        self.cells.append(cell)

    def get_cell(self, index: int):
        return self.cells[index]

    def __getitem__(self, index: int):
        return self.get_cell(index)

    def __str__(self) -> str:
        values = [c.value or "" for c in self.cells]
        return f"[{', '.join(values)}]"


class Column:
    def __init__(self, column_index: str, cells=None):
        self.column_index = column_index
        self.cells: list[Cell] = cells or []

    def add_cell(self, cell: Cell):
        self.cells.append(cell)

    def get_cell(self, index):
        return self.cells[index]


def build_row(row_index: int, col_count: int):
    row = Row(row_index=row_index)

    for i in range(col_count):
        new_cell = Cell(row_index=row_index, column_index=i)
        row.add_cell(new_cell)

    return row


def build_column(col_index: int, row_count: int):
    col = Column(column_index=col_index)

    for i in range(row_count):
        new_cell = Cell(row_index=i, column_index=col_index)
        col.add_cell(new_cell)

    return col


class Sheet:
    def __init__(self, dimensions: tuple[int, int]):
        col_count, row_count = dimensions
        rows = [build_row(i, col_count=col_count) for i in range(row_count)]
        cols = [build_column(i, row_count=row_count) for i in range(col_count)]
        self.rows = rows
        self.cols = cols

        self.dependency_graph: dict[str, Cell] = {}
        self.cells_dict = {}

    def get_cell(self, row_index: int, column_index: int):
        return self.rows[row_index].get_cell(column_index)

    def get_string_matrix(self) -> list[list[str]]:
        return [str(r) for r in self.rows]


if __name__ == "__main__":
    cell = Cell(column_index=0, row_index=0, formula="if(A1, b2, YY32)")
    print(cell.dependencies)
