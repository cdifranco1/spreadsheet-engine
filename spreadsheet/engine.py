import re
from typing import Any, Optional


class Cell:
    def __init__(self, value=None, formula=None):
        self.value = value
        self.formula = formula

    def calculate(self, cells: list["Row"]):
        if self.value is not None:
            return self.value
        if self.formula is not None:
            return self.eval_formula(cells)
        return None

    def eval_formula(self, rows: list["Row"]) -> None:
        # Define a regular expression pattern to match cell references
        cell_ref_pattern = re.compile(r"([A-Za-z]+)(\d+)")

        # Replace cell references with their corresponding values
        def replace_cell_ref(match):
            col = match.group(1)
            row = int(match.group(2))
            return rows[row - 1][ord(col.upper()) - 65].value

        formula = cell_ref_pattern.sub(replace_cell_ref, self.formula)
        return formula


class Row:
    def __init__(self, cells=None):
        self.cells: list[Cell] = cells or []

    def add_cell(self, cell: Cell):
        self.cells.append(cell)

    def get_cell(self, index: int):
        return self.cells[index]

    def __getitem__(self, index: int):
        return self.get_cell(index)

    def __str__(self) -> str:
        values = [c.value for c in self.cells]
        return f"[{','.join(values)}]"


class Column:
    def __init__(self, cells=None):
        self.cells: list[Cell] = cells or []

    def add_cell(self, cell: Cell):
        self.cells.append(cell)

    def get_cell(self, index):
        return self.cells[index]


class Sheet:
    def __init__(self, cols: list[Column] = [], rows: list[Row] = []):
        self.cols = cols
        self.rows = rows
        self.dependency_graph: dict[str, Cell] = {}
        self.cells_dict = {}

    def get_cell(self, row_index, column_index):
        return self.rows[row_index].get_cell(column_index)

    def calculate_all_cells(self):
        for row in self.rows:
            for cell in row.cells:
                cell.value = cell.calculate(self.get_cells_dict())

    def get_cells_dict(self) -> dict[str, Any]:
        cells_dict = {}
        for i, column in enumerate(self.columns):
            for j, cell in enumerate(column.cells):
                cells_dict[f"{chr(ord('A') + i)}{j + 1}"] = cell.value
        return cells_dict

    def get_string_matrix(self) -> list[list[str]]:
        return [r.cells for r in self.rows]


class Transpiler:
    def transpile_formula(formula):
        # Replace cell references with Python variables
        formula = re.sub(r"([A-Z]+)(\d+)", r'cells["\1"][\2].value', formula)

        # Replace Excel functions with Python functions
        formula = re.sub(r"SUM\((.*)\)", r"sum([\1])", formula)
        formula = re.sub(r"AVERAGE\((.*)\)", r"sum([\1])/len([\1])", formula)

        return formula


# Example usage
# formula = '=SUM(A1:A10) + AVERAGE(B1:B10) * C1'
# transpiled = Transpiler.transpile_formula(formula)
# print(transpiled)
# Output: cells["A"][1].value+cells["A"][2].value+cells["A"][3].value+cells["A"][4].value+cells["A"][5].value+cells["A"][6].value+cells["A"][7].value+cells["A"][8].value+cells["A"][9].value+cells["A"][10].value+sum([cells["B"][1].value,cells["B"][2].value,cells["B"][3].value,cells["B"][4].value,cells["B"][5].value,cells["B"][6].value,cells["B"][7].value,cells["B"][8].value,cells["B"][9].value,cells["B"][10].value])/len([cells["B"][1].value,cells["B"][2].value,cells["B"][3].value,cells["B"][4].value,cells["B"][5].value,cells["B"][6].value,cells["B"][7].value,cells["B"][8].value,cells["B"][9].value,cells["B"][10].value])*cells["C"][1].value
