from curva.framework.spreadsheet.group import Group
from curva.framework.spreadsheet.cell import Cell
from curva.spreadsheet.prelude.style import stylesheet

import copy


class PreludeGroup(Group):
    def __init__(self, parent_section, inputs, title, body, body_class_list, group_id, column_width=None):
        super().__init__(parent_section, inputs, group_id, [2, 0])

        self.add_row()

        header_cell = Cell(
            self,
            inputs,
            'header',
            {
                'text': title
            },
            set(['prelude_header']),
            column_width,
            stylesheet
        )
        self.add_cell(header_cell)

        for i, body_row in enumerate(body):
            if 'format' in body_row:
                body_row_format = body_row['format']
            else:
                body_row_format = body_class_list

            if 'repeat' in body_row:
                repeat_by = body_row['repeat']

                if type(repeat_by) == int:
                    for repeat_i in range(repeat_by):
                        self.add_row()

                        row_copy = copy.copy(body_row)
                        row_copy['text'] = row_copy['text'].format(index=repeat_i)

                        body_cell = Cell(
                            self,
                            self.inputs,
                            'body-{}-{}'.format(i, repeat_i),
                            row_copy,
                            body_row_format,
                            column_width,
                            stylesheet
                        )
                        self.add_cell(body_cell)
                elif type(repeat_by) == list:
                    for repeat_i, repeat_item in enumerate(repeat_by):
                        self.add_row()

                        row_copy = copy.copy(body_row)
                        row_copy['text'] = row_copy['text'].format(index=repeat_i, item=repeat_item)

                        body_cell = Cell(
                            self,
                            self.inputs,
                            'body-{}-{}'.format(i, repeat_i),
                            row_copy,
                            body_row_format,
                            column_width,
                            stylesheet
                        )
                        self.add_cell(body_cell)
            else:
                self.add_row()

                body_cell = Cell(
                    self,
                    self.inputs,
                    'body-{}'.format(i),
                    body_row,
                    body_class_list,
                    column_width,
                    stylesheet
                )
                self.add_cell(body_cell)
