import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

import render_style
import prelude_matrix

import copy

import re

class Spreadsheet():
    def __init__(self, inputs, fluxo_creditos, months, taxa_juros_sub, taxa_juros_anual_sub, tranche_list, sub_length, sen_length, fluxo_financeiro):
        self.inputs = inputs
        self.months = months
        self.fluxo_creditos = fluxo_creditos
        self.tranche_list = tranche_list
        self.fluxo_financeiro = fluxo_financeiro

        self.workbook = xlsxwriter.Workbook(inputs.output_path)
        self.workbook.set_size(1400, 1000)

        self.sheet = self.workbook.add_worksheet()
        self.sheet.hide_gridlines(2)
        self.sheet.set_default_row(18)

        self.sheet.insert_image(
            'F2',
            '{}/logos-logo.png'.format(self.inputs.appdata_path),
            {
                'x_scale': 0.75,
                'y_scale': 0.85,
                'x_offset': 10,
                'y_offset': -10
            }
        )

        self.formats = {}
        for key, style in render_style.formats.items():
            if style['is_template']:
                self.formats[key] = style['format']
            else:
                self.formats[key] = self.workbook.add_format(style['format'])

        self.p_matrix = prelude_matrix.create_matrix(
            self.inputs,
            taxa_juros_sub,
            taxa_juros_anual_sub,
            sub_length,
            sen_length
        )

        self.x_margin = 1

        self.prelude_x = 1
        self.prelude_y = 11
        self.prelude_width = len(self.p_matrix[0])

        self.fluxo_creditos_x = self.prelude_x + \
            self.prelude_width + \
            self.x_margin

        self.fluxo_creditos_y = 2
        self.fluxo_creditos_width = 3

        self.tranches_x = self.fluxo_creditos_x + \
            self.fluxo_creditos_width + \
            self.x_margin

        self.tranches_y = 2
        self.subordinate_tranche_width = 8
        self.normal_tranche_width = 7

        self.tranche_width = self.subordinate_tranche_width + \
            self.x_margin + \
            self.normal_tranche_width

        for _ in range(len(tranche_list) - 2):
            self.tranche_width += self.normal_tranche_width + self.x_margin

        self.fluxo_fin_x = self.tranches_x + self.tranche_width + self.x_margin
        self.fluxo_fin_y = 2
        self.fluxo_fin_width = 3

    def substitute_static(self, pos):
        groups = re.match(r'^([A-Z]+)(\d+)$', pos)
        return '${}${}'.format(groups[1], groups[2])

    def render_prelude(self):
        row_margin = 2

        spreadsheet_row = self.prelude_y

        title_height = 1

        self.position_matrix = {}

        for row in self.p_matrix:
            max_length = 1

            for cell_i, cell in enumerate(row):
                if 'title' in cell:
                    title, body, body_format = list(cell.values())

                    current_cell = cell_i + self.prelude_x

                    self.sheet.write(
                        spreadsheet_row,
                        current_cell,
                        title,
                        self.formats['prelude_header']
                    )

                    for body_row_i, body_row in enumerate(body):
                        current_row = spreadsheet_row + body_row_i + 1

                        adjusted_position_matrix = self.position_matrix.copy()
                        for a_title, position in adjusted_position_matrix.items():
                            adjusted_position_matrix[a_title] = self.substitute_static(
                                xl_rowcol_to_cell(
                                    position[0] + min(body_row_i, position[2]) + 1,
                                    position[1]
                                )
                            )

                        format_inputs = {
                            'i_next': xl_rowcol_to_cell(current_row, current_cell + 1),
                            'i_prev': xl_rowcol_to_cell(current_row, current_cell - 1),
                            'fluxo_fin_start': xl_rowcol_to_cell(self.fluxo_fin_y + 2, self.fluxo_fin_x + 1),
                            'fluxo_fin_end': xl_rowcol_to_cell(self.fluxo_fin_y + len(self.fluxo_financeiro) + 2, self.fluxo_fin_x + 1),
                            'prev_body': xl_rowcol_to_cell(current_row - 1, current_cell),
                            'fluxo_3_sum_terms': '{}:{}'.format(
                                xl_rowcol_to_cell(
                                    self.fluxo_creditos_y + 2, self.fluxo_creditos_x + 1
                                ),
                                xl_rowcol_to_cell(
                                    self.fluxo_creditos_y + 4, self.fluxo_creditos_x + 1
                                )
                            ),
                            'despesas_3_sum_terms': '{}:{}'.format(
                                xl_rowcol_to_cell(
                                    self.tranches_y + 6, self.tranches_x + 3
                                ),
                                xl_rowcol_to_cell(
                                    self.tranches_y + 8, self.tranches_x + 3
                                )
                            ),
                            **adjusted_position_matrix
                        }

                        self.sheet.write(
                            current_row,
                            current_cell,
                            body_row.format(**format_inputs),
                            self.formats[
                                body_format[
                                    min(body_row_i, len(body_format) - 1)
                                ]
                            ]
                        )

                    self.position_matrix[title.replace(' ', '_').replace('%', 'P')] = [
                        spreadsheet_row, current_cell, len(body) - 1
                    ]

            spreadsheet_row += max_length + title_height + row_margin

    def render_fluxo_creditos(self):
        self.sheet.merge_range(
            self.fluxo_creditos_y,
            self.fluxo_creditos_x,
            self.fluxo_creditos_y + 1,
            self.fluxo_creditos_x + self.fluxo_creditos_width - 1,
            'Fluxo de Créditos Imobiliários',
            self.formats['section_title']
        )

        for i, fluxo_row in enumerate(self.fluxo_creditos):
            row_offset = self.fluxo_creditos_y + i + 2

            current_index_format_template = copy.copy(self.formats['n_index'])
            current_fluxo_format_template = copy.copy(self.formats['fluxo'])
            current_date_format_template = copy.copy(self.formats['date'])

            if i == len(self.fluxo_creditos) - 1:
                current_index_format_template['bottom'] = 1
                current_fluxo_format_template['bottom'] = 1
                current_date_format_template['bottom'] = 1

            self.sheet.write(
                row_offset,
                self.fluxo_creditos_x,
                i + 1,
                self.workbook.add_format(current_index_format_template)
            )
            self.sheet.write(
                row_offset,
                self.fluxo_creditos_x + 1,
                fluxo_row,
                self.workbook.add_format(current_fluxo_format_template)
            )
            self.sheet.write(
                row_offset,
                self.fluxo_creditos_x + 2,
                self.months[i],
                self.workbook.add_format(current_date_format_template)
            )

    def render_empty_tranche_row(self, row, cell, width, border_balance):
        for i in range(width):
            border_template = self.workbook.add_format({})

            if i == 0 and (border_balance < 1):
                border_template.set_left(1)

            if i == width - 1 and (border_balance > -1):
                border_template.set_right(1)

            self.sheet.write(
                row,
                cell + i,
                '',
                border_template
            )

    def render_tranches(self):
        for tranche_i, tranche in enumerate(self.tranche_list):
            col_offset = self.tranches_x + \
                tranche_i * self.normal_tranche_width + \
                min(tranche_i, 1) + \
                self.x_margin * tranche_i

            self.sheet.merge_range(
                self.tranches_y,
                col_offset,
                self.tranches_y + 1,
                col_offset + self.subordinate_tranche_width - min(tranche_i, 1) - 1,
                'Tranche {}'.format(tranche.title),
                self.formats['section_title']
            )

            self.render_empty_tranche_row(
                self.tranches_y + 2,
                col_offset,
                self.subordinate_tranche_width - min(tranche_i, 1),
                0
            )
            self.render_empty_tranche_row(self.tranches_y + 3, col_offset, 1, -1)

            header_offset = 2

            self.sheet.write(
                self.tranches_y + 3,
                col_offset + header_offset,
                'Saldo Devedor',
                self.formats['tranche_header_col']
            )
            header_offset += 1

            if tranche_i == 0:
                self.sheet.write(
                    self.tranches_y + 3,
                    col_offset + header_offset,
                    'Despesas',
                    self.formats['tranche_header_col']
                )
                header_offset += 1

            self.sheet.write(
                self.tranches_y + 3,
                col_offset + header_offset,
                'Juros',
                self.formats['tranche_header_col']
            )
            header_offset += 1

            self.sheet.write(
                self.tranches_y + 3,
                col_offset + header_offset,
                'Amortiz',
                self.formats['tranche_header_col']
            )
            header_offset += 1

            self.sheet.write(
                self.tranches_y + 3,
                col_offset + header_offset,
                'PMT',
                self.formats['tranche_header_col']
            )
            header_offset += 1

            self.sheet.write(
                self.tranches_y + 3,
                col_offset + header_offset,
                '% AM',
                self.formats['east_tranche_header_col']
            )

            self.render_empty_tranche_row(
                self.tranches_y + 4,
                col_offset,
                self.subordinate_tranche_width - min(tranche_i, 1),
                0
            )

            self.render_empty_tranche_row(
                self.tranches_y + 5,
                col_offset,
                self.subordinate_tranche_width - min(tranche_i, 1),
                0
            )

            self.sheet.write(
                self.tranches_y + 5,
                col_offset,
                '=1',
                self.workbook.add_format(self.formats['n_index'])
            )

            date_format_template = copy.copy(self.formats['date'])
            date_format_template['right'] = 0

            self.sheet.write(
                self.tranches_y + 5,
                col_offset + 1,
                self.months[0],
                self.workbook.add_format(date_format_template)
            )

            quantity_format_template = copy.copy(self.formats['quantity'])

            self.sheet.write(
                self.tranches_y + 5,
                col_offset + 2,
                '={}'.format(self.inputs.total * self.inputs.razoes[tranche_i]),
                self.workbook.add_format(quantity_format_template)
            )

            row_offset = self.tranches_y + 6
            for row_i, row in enumerate(tranche.row_list):
                index_format_template = copy.copy(self.formats['n_index'])
                percentage_format_template = copy.copy(self.formats['percentage'])

                taxa_juros_pos = copy.copy(self.position_matrix[tranche.title])
                taxa_juros_pos[0] = taxa_juros_pos[0] + 1
                taxa_juros_pos = self.substitute_static(
                    xl_rowcol_to_cell(
                        taxa_juros_pos[0],
                        taxa_juros_pos[1]
                    )
                )

                pmt_proper_pos = copy.copy(self.position_matrix['P_PMT'])
                pmt_proper_pos[0] = pmt_proper_pos[0] + 1
                pmt_proper_pos = self.substitute_static(
                    xl_rowcol_to_cell(
                        pmt_proper_pos[0],
                        pmt_proper_pos[1]
                    )
                )

                if row_i == len(tranche.row_list) - 1:
                    index_format_template['bottom'] = 1
                    date_format_template['bottom'] = 1
                    quantity_format_template['bottom'] = 1
                    percentage_format_template['bottom'] = 1

                col_inner_offset = col_offset

                self.sheet.write(
                    row_offset,
                    col_inner_offset,
                    '={}'.format(row_i + 2),
                    self.workbook.add_format(index_format_template)
                )
                col_inner_offset += 1

                self.sheet.write(
                    row_offset,
                    col_inner_offset,
                    self.months[row_i + 1],
                    self.workbook.add_format(date_format_template)
                )
                col_inner_offset += 1

                formatted_formulae = {
                    'prev_saldo': xl_rowcol_to_cell(row_offset - 1, col_offset + 2),
                    'taxa_juros': taxa_juros_pos,
                    'despesas': xl_rowcol_to_cell(row_offset, col_offset + 3),
                    'juros': xl_rowcol_to_cell(row_offset, col_offset + 4 - min(tranche_i, 1)),
                    'pmt': xl_rowcol_to_cell(row_offset, col_offset + 6 - min(tranche_i, 1)),
                    'F_i': xl_rowcol_to_cell(
                        self.fluxo_creditos_y + 2 + row_i,
                        self.fluxo_creditos_x + 1
                    ),
                    'pmt_proper': pmt_proper_pos,
                    'pmt_next': xl_rowcol_to_cell(
                        row_offset,
                        col_offset + self.subordinate_tranche_width + 6 - min(tranche_i, 1)
                    ),
                    'amort': xl_rowcol_to_cell(row_offset, col_offset + 5 - min(tranche_i, 1)),
                    'row_sum': '-'.join([
                        str(xl_rowcol_to_cell(
                            row_offset,
                            col_offset - 3 - i * (self.normal_tranche_width + 1)
                        ))
                    for i in range(len(self.tranche_list) - 1)])
                }

                self.sheet.write(
                    row_offset,
                    col_inner_offset,
                    '=' + row.formulae['saldo'].format(**formatted_formulae),
                    self.workbook.add_format(quantity_format_template)
                )
                col_inner_offset += 1

                if tranche_i == 0:
                    self.sheet.write(
                        row_offset,
                        col_inner_offset,
                        '={}'.format(row.despesas),
                        self.workbook.add_format(quantity_format_template)
                    )
                    col_inner_offset += 1

                self.sheet.write(
                    row_offset,
                    col_inner_offset,
                    '=' + row.formulae['juros'].format(**formatted_formulae),
                    self.workbook.add_format(quantity_format_template)
                )
                col_inner_offset += 1

                self.sheet.write(
                    row_offset,
                    col_inner_offset,
                    '=' + row.formulae['amort'].format(**formatted_formulae),
                    self.workbook.add_format(quantity_format_template)
                )
                col_inner_offset += 1

                self.sheet.write(
                    row_offset,
                    col_inner_offset,
                    '=' + row.formulae['pmt'].format(**formatted_formulae),
                    self.workbook.add_format(quantity_format_template)
                )
                col_inner_offset += 1

                self.sheet.write(
                    row_offset,
                    col_inner_offset,
                    '={}/{}'.format(
                        formatted_formulae['amort'],
                        formatted_formulae['prev_saldo']
                    ),
                    self.workbook.add_format(percentage_format_template)
                )

                row_offset += 1

    def render_fluxo_financeiro(self):
        self.sheet.merge_range(
            self.fluxo_fin_y,
            self.fluxo_fin_x,
            self.fluxo_fin_y + 1,
            self.fluxo_fin_x + 2,
            'Fluxo Financeiro',
            self.formats['section_title']
        )

        for row_i, row in enumerate(self.fluxo_financeiro):
            row_offset = self.fluxo_fin_y + 2 + row_i
            tranche_displacement_offset = 3

            n_index_format_template = copy.copy(self.formats['n_index'])
            quantity_format_template = copy.copy(self.formats['quantity'])
            date_format_template = copy.copy(self.formats['date'])

            if row_i == len(self.fluxo_financeiro) - 1:
                n_index_format_template['bottom'] = 1
                quantity_format_template['bottom'] = 1
                date_format_template['bottom'] = 1

            self.sheet.write(
                row_offset,
                self.fluxo_fin_x,
                row_i + 1,
                self.workbook.add_format(n_index_format_template)
            )

            quantity = '0'
            if row_i == 0:
                quantity = str(-self.inputs.total)
            elif row_i > self.inputs.c_period:
                quantity = '+'.join([
                    '{}+{}'.format(
                        xl_rowcol_to_cell(
                            row_offset + tranche_displacement_offset,
                            self.tranches_x + i * (self.normal_tranche_width + 1) + 4
                        ),
                        xl_rowcol_to_cell(
                            row_offset + tranche_displacement_offset,
                            self.tranches_x + i * (self.normal_tranche_width + 1) + 5
                        )
                    )
                    for i in range(len(self.tranche_list))
                ])
            self.sheet.write(
                row_offset,
                self.fluxo_fin_x + 1,
                '=' + quantity,
                self.workbook.add_format(quantity_format_template)
            )

            self.sheet.write(
                row_offset,
                self.fluxo_fin_x + 2,
                self.months[row_i],
                self.workbook.add_format(date_format_template)
            )

    def resize_columns(self):
        column_widths = [6, 18, 15.5, 14, 17.5, 19, 12, 13.5,
                         8, 6, 11, 8, 4, 6, 8, 13, 10, 12, 12, 11, 10, 4]

        for _ in range(len(self.tranche_list) - 1):
            column_widths += [6, 8, 13, 12, 12, 11, 10, 4]

        column_widths += [6, 14, 8]

        for i, width in enumerate(column_widths):
            self.sheet.set_column(i, i, width)

    def render_file(self):
        self.workbook.close()
