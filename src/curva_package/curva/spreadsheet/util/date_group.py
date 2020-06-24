from curva.framework.spreadsheet.group import Group
from curva.framework.spreadsheet.cell import Cell
from curva.spreadsheet.style import stylesheet


class DateGroup(Group):
    def __init__(self, parent_section, inputs, length, class_list):
        super().__init__(parent_section, inputs, 'date', [0, 0])
        
        for i, date in enumerate(inputs.get('flux-months')):
            self.add_row()

            cell = Cell(
                self,
                self.inputs,
                f'body_{i}',
                {
                    'text': f'{date}'
                },
                set(['date', *class_list]),
                8,
                stylesheet
            )
            self.add_cell(cell)

            if i >= length:
                break

        self.inject_style(lambda i: 's' if i == -1 else None, -1)
