from curva.framework.spreadsheet.group import Group
from curva.spreadsheet.style import stylesheet


class EmptyGroup(Group):
    def __init__(self, dimensions=(1, 1), borders=set(), column_width=None):
        self.id = None

        self.dimensions = dimensions
        self.borders = borders
        self.column_width = column_width

    def set_bounds(self, vertical_offset, horizontal_offset):
        self.vertical_offset = vertical_offset
        self.horizontal_offset = horizontal_offset

    def get_dimensions(self):
        return self.dimensions

    def add_borders(self, row, col, borders):
        stylesheet_borders = {k: v for d in borders for k, v in stylesheet[d].items()}
        self.sheet.write(
            self.vertical_offset + row,
            self.horizontal_offset + col,
            '',
            self.workbook.add_format(stylesheet_borders)
        )

    def render(self, sheet, workbook):
        self.sheet, self.workbook = sheet, workbook

        for row in range(self.dimensions[0]):
            for col in range(self.dimensions[1]):
                cell_borders = set()
                if row == 0 and 'n' in self.borders:
                    cell_borders.add('n')
                if col == 0 and 'w' in self.borders:
                    cell_borders.add('w')
                if row == self.dimensions[0] - 1 and 's' in self.borders:
                    cell_borders.add('s')
                if col == self.dimensions[1] - 1 and 'e' in self.borders:
                    cell_borders.add('e')
                self.add_borders(row, col, cell_borders)

        if self.column_width:
            self.sheet.set_column(
                self.horizontal_offset,
                self.horizontal_offset + self.dimensions[1],
                self.column_width
            )


