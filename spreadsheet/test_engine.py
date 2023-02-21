import unittest
from spreadsheet.engine import Row, Cell, Sheet, Column


class TestSpreadsheet(unittest.TestCase):
    # def test_calculate_cell(self):
    #     cell = Cell(formula="2+2")
    #     self.assertEqual(cell.calculate({}), 4)

    # def test_add_row(self):
    #     sheet = Sheet()
    #     row = Row(cells=[Cell(value=1), Cell(value=2)])
    #     sheet.add_row(row)
    #     self.assertEqual(len(sheet.rows), 1)

    # def test_add_column(self):
    #     sheet = Sheet()
    #     column = Column(cells=[Cell(value=1), Cell(value=2)])
    #     sheet.add_column(column)
    #     self.assertEqual(len(sheet.columns), 1)

    # def test_get_cell(self):
    #     sheet = Sheet()
    #     row = Row(cells=[Cell(value=1), Cell(value=2)])
    #     sheet.add_row(row)
    #     cell = sheet.get_cell(0, 1)
    #     self.assertEqual(cell.value, 2)

    # def test_calculate_all_cells(self):
    #     sheet = Sheet()
    #     row1 = Row(cells=[Cell(formula="2+2"), Cell(value=3)])
    #     row2 = Row(cells=[Cell(formula="A1*2"), Cell(formula="B1*3")])
    #     sheet.add_row(row1)
    #     sheet.add_row(row2)
    #     sheet.calculate_all_cells()
    #     self.assertEqual(sheet.get_cell(0, 0).value, 4)
    #     self.assertEqual(sheet.get_cell(1, 0).value, 8)
    #     self.assertEqual(sheet.get_cell(1, 1).value, 9)

    def test_eval_formula(self):
        # Define a simple test case with two cells
        cell_matrix = [
            Row([Cell('3'), Cell('5')]),   # Row 1: 3 + 5 = 8
            Row([Cell('2'), Cell('4')]),   # Row 2: 2 * 4 = 8
            Row([Cell('1'), Cell('3')]),    # Row 3: 1 ^ 2 = 1
        ]

        cell1 = Cell(formula="=A1+B1")

        # Test the eval_formula function with the test case
        print(cell1.eval_formula(cell_matrix))
        # print(eval_formula('A2*B2', cell_matrix))
        # assert eval_formula('A3^2', cell_values) == 1
        # assert eval_formula('SUM(A1:B1)', cell_values) == 8
        # assert eval_formula('SUM(A1:B2)', cell_values) == 20


if __name__ == '__main__':
    unittest.main()
