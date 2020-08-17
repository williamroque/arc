from curva.framework.spreadsheet.group import Group
from curva.framework.spreadsheet.cell import Cell
from curva.spreadsheet.style import stylesheet
from curva.spreadsheet.taxa_emissao.style import stylesheet as taxa_stylesheet


class ColumnGroup(Group):
    def __init__(self, parent_section, inputs, group_id, header, is_bold, border=None):
        super().__init__(parent_section, inputs, group_id, [0, 0])

        self.add_row()

        cell = Cell(
            self,
            self.inputs,
            'header',
            {'text': header['title']},
            {'taxa_text'},
            header['column_width'],
            {
                **stylesheet,
                **taxa_stylesheet
            }
        )
        if border:
            cell.add_class(border)
        self.add_cell(cell)


class SeriesHeaderGroup(Group):
    def __init__(self, parent_section, title, group_id):
        super().__init__(parent_section, None, group_id, [0, 0])

        self.title = title

    def get_dimensions(self):
        return (1, 4)

    def query(self, _):
        return None

    def render(self, sheet, workbook):
        sheet.merge_range(
            self.vertical_offset,
            self.horizontal_offset,
            self.vertical_offset,
            self.horizontal_offset + 3,
            self.title,
            workbook.add_format(
                {
                    **taxa_stylesheet['series_header'],
                    **stylesheet['e'],
                    **stylesheet['w']
                }
            )
        )
