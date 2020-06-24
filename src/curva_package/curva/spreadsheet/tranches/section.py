from curva.framework.spreadsheet.section import Section
from curva.framework.spreadsheet.cell import Cell
from curva.spreadsheet.util.header_group import HeaderGroup
from curva.spreadsheet.util.empty_group import EmptyGroup
from curva.spreadsheet.util.empty_cell import EmptyCell
from curva.spreadsheet.tranches.column_group import ColumnGroup
from curva.spreadsheet.style import stylesheet
from curva.spreadsheet.tranches.style import stylesheet as tranches_stylesheet


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
                    'data': self.inputs.get('flux-months')[row_i],
                    'original_saldo': tranche.saldo_original,
                    'prev_saldo': '@0',
                    'despesas': '@1',
                    'juros': '@2',
                    'amort': '@3',
                    'pmt': '@4',
                    'taxa_juros': '@5',
                    'F_i': '@6',
                    'pmt_proper': '@7',
                    'pmt_next': '@8',
                    'row_sum': '-'.join([f'@{i + 9}' for i in range(len(tranche_list[:-1]))])
                }

                row_cell = Cell(
                    column_group,
                    self.inputs,
                    f'row_{row_i}',
                    {
                        'text': column['formula'].format(**substitution_map),
                        'references': [
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
                                'path': ['prelude', f'{self.id}-juros', 0],
                                'static': True
                            },
                            {
                                'path': ['fluxo-creditos', 'value', f'row_{row_i - 1}'],
                                'static': False
                            },
                            {
                                'path': ['prelude', 'pmt-proper', 0],
                                'static': True
                            },
                            {
                                'path': [
                                    tranche_list[tranche_i + 1].id if tranche_i < len(tranche_list) - 1 else None,
                                    'pmt',
                                    f'row_{row_i}'
                                ],
                                'static': False
                            },
                            *[{
                                'path': [tranche.id, 'pmt', f'row_{row_i}'],
                                'static': False
                            } for tranche in tranche_list[:-1]]
                        ]
                    },
                    set([
                        *column['style'],
                        *([border] if border else []),
                        *(['s'] if row_i == len(tranche.row_list) - 1 else [])
                    ]),
                    column['column_width'],
                    {
                        **stylesheet,
                        **tranches_stylesheet
                    }
                )
                column_group.add_cell(row_cell)

            self.add_group(column_group)

