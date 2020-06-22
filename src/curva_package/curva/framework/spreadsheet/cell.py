import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

import re


class Cell():
    def __init__(self, parent_group, inputs, cell_id, content, class_list, column_width, stylesheet):
        self.parent_group = parent_group
        self.inputs = inputs

        self.id = cell_id
        self.content = content
        self.class_list = class_list

        self.column_width = column_width

        self.stylesheet = stylesheet

        self.format = {}
        self.compile_format()

    def compile_format(self):
        for class_name in self.class_list:
            if class_name in self.stylesheet:
                self.format = {
                    **self.format,
                    **self.stylesheet[class_name]
                }

    def add_class(self, class_name):
        if class_name != None:
            self.class_list.add(class_name)
            self.compile_format()

    def set_bounds(self, vertical_offset, horizontal_offset):
        self.vertical_offset = vertical_offset
        self.horizontal_offset = horizontal_offset

    def get_reference(self):
        return xl_rowcol_to_cell(self.vertical_offset, self.horizontal_offset)

    def render(self, sheet, workbook):
        text = self.content['text']

        if 'references' in self.content:
            for i, reference in enumerate(self.content['references']):
                spreadsheet = self.parent_group.parent_section.parent_sheet

                path = reference['path']

                target_section = spreadsheet.query(path[0])
                target_group = target_section.query(path[1])
                target_cell = target_group.query(path[2])

                target_reference = target_cell.get_reference()

                if reference['static']:
                    col, row = re.search(r'([A-Za-z]+)(\d+)', target_reference).groups()
                    target_reference = f'${col}${row}'

                text = text.replace(
                    f'@{i}',
                    target_reference
                )

        # text = text.format(**self.inputs)

        if self.column_width:
            sheet.set_column(
                self.horizontal_offset,
                self.horizontal_offset,
                self.column_width
            )

        sheet.write(
            self.vertical_offset,
            self.horizontal_offset,
            text,
            workbook.add_format(self.format)
        )
