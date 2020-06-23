from curva.framework.spreadsheet.group import Group
from curva.framework.spreadsheet.cell import Cell
from curva.spreadsheet.tranches.style import stylesheet


class ColumnHeaderGroup(Group):
    def __init__(self, parent_section, inputs, headers):
        super().__init__(parent_section, inputs, 'column-headers', [0, 0])

        self.add_row()

        for header in headers:
            cell = Cell(
                self,
                self.inputs,
                header['id'],
                header['title'],
                set(['tranche_column_header']),
                header['column-width'],
                stylesheet
            )
            self.add_cell(cell)