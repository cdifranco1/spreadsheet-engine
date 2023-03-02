from typing import Any
from graph.dependency_graph import DAG
from parser.parser import Scanner, Parser
import re


class Cell:
    def __init__(self, column_index: int, row_index: int, value=None, formula=None):
        self.column_index = column_index
        self.row_index = row_index
        self.cell_ref = get_cell_ref(row=row_index, column=column_index)
        self._value = value

        self._is_dirty = False

        self.formula = formula
        self.dependencies = self.get_formula_deps()

    def get_formula_deps(self) -> list[str]:
        return (
            [col + row for col, row in self.extract_formula_deps()]
            if self.formula
            else []
        )

    def get_value(self) -> Any:
        if self._is_dirty or not self._value:
            return self.formula

        return self._value

    def update_formula(self, new_formula: str) -> list[str]:
        self.formula = new_formula
        self._is_dirty = True
        self.dependencies = self.get_formula_deps()
        return self.dependencies

    def calculate(self, worksheet: "Sheet"):
        if self._value is not None and not self._is_dirty:
            return self._value
        if self.formula is not None:
            self._value = self.eval_formula(worksheet=worksheet)
            return self._value
        return None

    def eval_formula(self, worksheet: "Sheet") -> Any:
        scanner = Scanner(self.formula)
        tokens = scanner.scan_tokens()
        scanner.print_tokens()
        parse_tree = Parser(tokens).parse()
        dependency_table = {
            ref: worksheet.get_cell(ref).calculate(worksheet=worksheet)
            for ref in self.dependencies
        }
        return parse_tree.eval(cell_ref_table=dependency_table)

    def get_top_sorted_deps(self) -> list[str]:
        pass

    def extract_formula_deps(self) -> list[str]:
        regex = re.compile("([A-Za-z]+)(\d+)")
        result = regex.findall(self.formula)
        return result

    def has_dependencies(self) -> bool:
        return len(self.dependencies) > 0

    def __str__(self) -> str:
        return f"Cell(cell_ref={self.cell_ref}, formula={self.formula}, value={self._value})"


class Row:
    def __init__(self, row_index: int, cells=None):
        self.row_index = row_index
        self.cells: list[Cell] = cells or []

    # TODO: balance out columns
    def add_cell(self, cell: Cell):
        self.cells.append(cell)

    def get_cell(self, index: int):
        return self.cells[index]

    def __getitem__(self, index: int):
        return self.get_cell(index)

    def __str__(self) -> str:
        values = [
            str(c.get_value()) if c.get_value() is not None else "" for c in self.cells
        ]
        return f"[{', '.join(values)}]"


class Column:
    def __init__(self, column_index: str, cells=None):
        self.column_index = column_index
        self.cells: list[Cell] = cells or []

    # TODO: balance out rows
    def add_cell(self, cell: Cell):
        self.cells.append(cell)

    def get_cell(self, index):
        return self.cells[index]


def build_row(row_index: int, col_count: int) -> Row:
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
        self.rows = [build_row(i, col_count=col_count) for i in range(row_count)]
        self.cols = [build_column(i, row_count=row_count) for i in range(col_count)]
        self.dependency_graph = DAG()

    def get_cell(self, cell_ref: str):
        col_i, row_i = ref_to_index(cell_ref)
        return self.rows[row_i].get_cell(col_i)

    # TODO: Check for cycles
    def update_cell_formula(self, cell_ref: str, formula: str) -> None:
        column_index, row_index = ref_to_index(cell_ref)
        cell: Cell = self.rows[row_index].get_cell(column_index)
        dependency_refs = cell.update_formula(formula)
        predecessors = [self.get_cell(cell_ref) for cell_ref in dependency_refs]
        self.dependency_graph.add(cell, *predecessors)

    def get_string_matrix(self) -> list[list[str]]:
        return [str(r) for r in self.rows]


def get_cell_ref(row, column):
    column_letters = ""
    while column >= 0:
        column_letters = chr((column % 26) + ord("A")) + column_letters
        column = column // 26 - 1
    return column_letters + str(row + 1)


def ref_to_index(ref: str):
    """
    Takes in a cell reference and returns zero-based column and row index tuple.

    Example:
        col_index, row_index = ref_to_index("A5")

        col_index == 0
        row_index == 4
    """
    regex = re.compile("([A-Za-z]+)(\d+)")
    res = regex.match(ref)

    col = res.group(1)
    row = res.group(2)

    index = 0
    for i in range(len(col)):
        char = ref[i].upper()
        char_index = ord(char) - ord("A") + 1
        addition = char_index * (26 ** (len(col) - i - 1))
        index += addition
    return index - 1, int(row) - 1


if __name__ == "__main__":
    sheet = Sheet((10, 10))

    sheet.update_cell_formula("A1", "IF(AND(2 * 2 < 5, 3 * 3 > 6), 200, 400)")
    sheet.update_cell_formula("A2", "100 > C5")  # TRUE
    sheet.update_cell_formula("A5", "200 * 2")  # should be 400
    sheet.update_cell_formula("B10", "3 ^ C5")  # 9
    sheet.update_cell_formula("C5", "2")  # == 2

    cell = sheet.get_cell("A1")
    print(f"Before calc...")
    print(f"A1 CELL: {cell}")
    # print(f"A2 CELL: {sheet.get_cell('A2')}")
    result = cell.calculate(sheet)
    print(result)

    print()
    print(f"After calc...")
    print(f"A1 CELL: {cell}")
    # print(f"A2 CELL: {sheet.get_cell('A2')}")

    cells = sheet.get_string_matrix()
    print(cells)
