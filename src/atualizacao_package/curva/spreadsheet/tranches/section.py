import re

from curva.framework.spreadsheet.section import Section
from curva.framework.spreadsheet.cell import Cell
from curva.spreadsheet.util.header_group import HeaderGroup
from curva.spreadsheet.util.empty_group import EmptyGroup
from curva.spreadsheet.util.empty_cell import EmptyCell
from curva.spreadsheet.tranches.column_group import ColumnGroup
from curva.spreadsheet.style import stylesheet
from curva.spreadsheet.tranches.style import stylesheet as tranches_stylesheet

import datetime
import locale

locale.setlocale(locale.LC_TIME, 'pt_BR')
epoch = datetime.datetime(1899, 12, 30)


class TrancheSection(Section):
    def __init__(self, parent_sheet, inputs, tranche, tranche_i):
        super().__init__(parent_sheet, inputs, tranche.id, [0, 0], [2, 0])

        self.add_row()

        column_count = len(tranche.row_list[0].get_values())

        header_group = HeaderGroup(self, tranche.title, 'header', 2, column_count)
        self.add_group(header_group)

        self.add_row()

        empty_group = EmptyGroup((1, column_count), set(['w', 'e']))
        self.add_group(empty_group)

        self.add_row()

        columns = tranche.row_list[0].get_columns().items()
        for i, (column_id, column) in enumerate(columns):
            border = 'w' if i == 0 else ('e' if i == len(columns) - 1 else None)

            column_group = ColumnGroup(
                self,
                self.inputs,
                column_id,
                column,
                border
            )

            column_group.add_row()

            column_group.add_cell(
                EmptyCell(
                    set([*(border if border else [])]),
                    stylesheet
                )
            )

            for row_i, row in enumerate(tranche.row_list):
                column_group.add_row()

                column = row.get_columns()[column_id]

                tranche_list = self.inputs.get('tranche-list')
                substitution_map = {
                    'i': row_i + 1,
                    'data': '={}'.format((datetime.datetime.strptime(self.inputs.get('flux-months')[row_i], '%b-%y') - epoch).days),
                    'valor_total': '@0',
                    'razao': '@1',
                    'prev_saldo': '@2',
                    'despesas': '@3',
                    'juros': '@4',
                    'amort': '@5',
                    'pmt': '@6',
                    'taxa_juros': '@7',
                    'amort_perc': '@8'
                }

                formula = column['formula']

                substitution_map = {
                    **substitution_map,
                    **formula[1]
                }

                if type(column['style']) == dict:
                    style = set()
                    for pattern in column['style']:
                        if re.match(pattern, formula[2]):
                            style |= column['style'][pattern]
                else:
                    style = column['style']

                if border:
                    style.add(border)

                if row_i == len(tranche.row_list) - 1:
                    style.add('s')

                ipca_periodo = self.inputs.get('ipca-periodo')['ipca']
                try:
                    ipca_index = ipca_periodo.index(self.get_year(row_i))
                except ValueError:
                    ipca_index = len(ipca_periodo) - 1

                row_cell = Cell(
                    column_group,
                    self.inputs,
                    f'row_{row_i}',
                    {
                        'text': column['formula'][0].format_map(substitution_map),
                        'references': [
                            {
                                'path': ['prelude', 'valor-total', 0],
                                'static': True
                            },
                            {
                                'path': ['prelude', 'razoes', len(tranche_list) - tranche_i - 1],
                                'static': True
                            },
                            {
                                'path': [self.id, 'saldo', f'row_{row_i - 1}'],
                                'static': False
                            },
                            {
                                'path': [self.id, 'despesas', f'row_{row_i}'],
                                'static': False
                            },
                            {
                                'path': [self.id, 'juros', f'row_{row_i}'],
                                'static': False
                            },
                            {
                                'path': [self.id, 'amort', f'row_{row_i}'],
                                'static': False
                            },
                            {
                                'path': [self.id, 'pmt', f'row_{row_i}'],
                                'static': False
                            },
                            {
                                'path': ['taxa-emissao', f'mensal-{self.id}', f'row_{ipca_index}'],
                                'static': True
                            },
                            {
                                'path': [self.id, 'amort_perc', f'row_{row_i}'],
                                'static': True
                            }
                        ]
                    },
                    style,
                    column['column_width'],
                    {
                        **stylesheet,
                        **tranches_stylesheet
                    }
                )
                column_group.add_cell(row_cell)

            self.add_group(column_group)

    def get_year(self, i):
        MONTHS = list(map(lambda x: x.lower(), 'Jan|Fev|Mar|Abr|Mai|Jun|Jul|Ago|Set|Out|Nov|Dez'.split('|')))
        month, year = self.inputs.get('curve')['starting-date'].split('/')

        monthIndex = MONTHS.index(month.lower())

        year = int(year)
        if (i < 0):
            year -= Math.ceil(-((monthIndex + i) / 12))
        else:
            year += int((monthIndex + i) / 12)

        return str(year)

