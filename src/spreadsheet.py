import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

import render_style
import prelude_matrix


class Spreadsheet():
    def __init__(self, inputs, taxa_juros_sub, taxa_juros_anual_sub, tranche_list, fluxo_financeiro, sub_length, sen_length):
        self.inputs = inputs
        self.tranche_list = tranche_list
        self.fluxo_financeiro = fluxo_financeiro

        self.workbook = xlsxwriter.Workbook(inputs.output_path)
        self.workbook.set_size(1400, 1000)

        self.sheet = self.workbook.add_worksheet()
        self.sheet.hide_gridlines(2)
        self.sheet.set_default_row(18)

        self.sheet.insert_image(
            'F2',
            '../logos-logo.png',
            {
                'x_scale': 0.75,
                'y_scale': 0.85,
                'x_offset': 10,
                'y_offset': -10
            }
        )

        self.formats = {}
        for key, style in render_style.formats.items():
            self.formats[key] = self.workbook.add_format(style)

        self.p_matrix = prelude_matrix.create_matrix(self.inputs, taxa_juros_sub, taxa_juros_anual_sub, sub_length, sen_length)

        self.x_margin = 1

        self.prelude_x = 1
        self.prelude_y = 11
        self.prelude_width = len(self.p_matrix[0])

        self.fluxo_creditos_x = self.prelude_x + self.prelude_width + self.x_margin
        self.fluxo_creditos_y = 2
        self.fluxo_creditos_width = 3

        self.tranches_x = self.fluxo_creditos_x + self.fluxo_creditos_width + self.x_margin
        self.tranches_y = 2
        self.subordinate_tranche_width = 8
        self.normal_tranche_width = 7
        self.tranche_width = self.subordinate_tranche_width + self.x_margin + self.normal_tranche_width

        for _ in range(len(tranche_list) - 2):
            self.tranche_width += self.normal_tranche_width + self.x_margin

        self.fluxo_fin_x = self.tranches_x + self.tranche_width + self.x_margin
        self.fluxo_fin_y = 2
        self.fluxo_fin_width = 3


    def render_prelude(self):
        row_offset = 11
        cell_offset = 1

        row_margin = 2

        spreadsheet_row = row_offset

        title_height = 1

        position_matrix = {}

        for row in self.p_matrix:
            max_length = 1

            for cell_i, cell in enumerate(row):
                if 'title' in cell:
                    title, body, body_format = list(cell.values())

                    current_cell = cell_i + cell_offset

                    self.sheet.write(
                        spreadsheet_row,
                        current_cell,
                        title,
                        self.formats['prelude_header']
                    )

                    for body_row_i, body_row in enumerate(body):
                        current_row = spreadsheet_row + body_row_i + 1

                        adjusted_position_matrix = position_matrix.copy()
                        for a_title, position in adjusted_position_matrix.items():
                            adjusted_position_matrix[a_title] = xl_rowcol_to_cell(position[0] + min(body_row_i, position[2]) + 1, position[1])

                        format_inputs = {
                            'i_next': xl_rowcol_to_cell(current_row, current_cell + 1),
                            'i_prev': xl_rowcol_to_cell(current_row, current_cell - 1),
                            'fluxo_fin_start': xl_rowcol_to_cell(self.fluxo_fin_y + 2, self.fluxo_fin_x + 2),
                            'fluxo_fin_end': xl_rowcol_to_cell(self.fluxo_fin_y + len(self.fluxo_financeiro) + 3, self.fluxo_fin_x + 2),
                            'prev_body': xl_rowcol_to_cell(current_row - 1, current_cell),
                            'fluxo_3_sum': '{}:{}'.format(
                                xl_rowcol_to_cell(self.fluxo_creditos_y + 2, self.fluxo_creditos_x + 1),
                                xl_rowcol_to_cell(self.fluxo_creditos_y + 5, self.fluxo_creditos_x + 1)
                            ),
                            'despesas_3_sum': '{}:{}'.format(
                                xl_rowcol_to_cell(self.tranches_y + 6, self.tranches_x + 3),
                                xl_rowcol_to_cell(self.tranches_y + 9, self.tranches_x + 3)
                            ),
                            **adjusted_position_matrix
                        }

                        self.sheet.write(
                            current_row,
                            current_cell,
                            body_row.format(**format_inputs),
                            self.formats[body_format[min(body_row_i, len(body_format) - 1)]]
                        )

                    position_matrix[title.replace(' ', '_').replace('%', 'P')] = (spreadsheet_row, current_cell, len(body) - 1)

            spreadsheet_row += max_length + title_height + row_margin

    def render_tranches(self):
        pass

    def resize_columns(self):
        column_widths = [6, 18, 15.5, 14, 17.5, 19, 12, 13.5,
                        8, 6, 11, 8, 4, 6, 8, 13, 10, 12, 12, 11, 10, 4]

        for _ in range(len(self.tranche_list)):
            column_widths += [6, 8, 13, 12, 12, 11, 10, 4]

        column_widths += [6, 6, 12]

        for i, width in enumerate(column_widths):
            self.sheet.set_column(i, i, width)

    def render_file(self):
        self.workbook.close()
