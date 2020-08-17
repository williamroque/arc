from curva.framework.spreadsheet.cell import Cell
from curva.framework.spreadsheet.section import Section
from curva.spreadsheet.util.header_group import HeaderGroup
from curva.spreadsheet.util.empty_group import EmptyGroup
from curva.spreadsheet.taxa_emissao.group import ColumnGroup, SeriesHeaderGroup
from curva.spreadsheet.style import stylesheet
from curva.spreadsheet.taxa_emissao.style import stylesheet as taxa_stylesheet


class TaxaEmissaoSection(Section):
    def __init__(self, parent_sheet, inputs):
        super().__init__(
            parent_sheet,
            inputs,
            'taxa-emissao',
            [0, 1],
            [2, 1]
        )

        layers_count = self.inputs.get('curve')['mezanine-layers-count'] + 2

        self.add_row()

        header_group = HeaderGroup(self, 'Taxa Emissão', 'header', 2, 4)
        self.add_group(header_group)

        for tranche_i, tranche in enumerate(self.inputs.get('tranche-list')[::-1]):
            self.add_row()

            column_header_group = SeriesHeaderGroup(self, tranche.title, f'header_{tranche.id}')
            self.add_group(column_header_group)

            self.add_row()

            periodo_group = ColumnGroup(
                self,
                self.inputs,
                f'periodo-{tranche.id}',
                {
                    'title': 'Periodo',
                    'column_width': 9
                },
                True,
                'w'
            )

            ipca_anual_group = ColumnGroup(
                self,
                self.inputs,
                f'ipca-anual-{tranche.id}',
                {
                    'title': 'IPCA Anual',
                    'column_width': 11
                },
                False
            )

            ipca_ta_group = ColumnGroup(
                self,
                self.inputs,
                f'ipca-ta-{tranche.id}',
                {
                    'title': 'IPCA + T.A.',
                    'column_width': 9.5
                },
                False
            )

            mensal_group = ColumnGroup(
                self,
                self.inputs,
                f'mensal-{tranche.id}',
                {
                    'title': 'IPCA + T.A.',
                    'column_width': 9.5
                },
                False,
                'e'
            )

            for i, year in enumerate(self.inputs.get('ipca-periodo')['ipca']):
                periodo_group.add_row()
                periodo_group.add_cell(Cell(
                    periodo_group,
                    self.inputs,
                    f'row_{i}',
                    {
                        'text': f'={year}'
                    },
                    {'taxa_text', 'w'},
                    None,
                    {
                        **stylesheet,
                        **taxa_stylesheet
                    }
                ))

                ipca_anual_group.add_row()
                ipca_anual_group.add_cell(Cell(
                    ipca_anual_group,
                    self.inputs,
                    f'row_{i}',
                    {
                        'text': '={}'.format(self.inputs.get('ipca-anual')['ipca'][i])
                    },
                    {'taxa_text', 'taxa_percentage_2_0'},
                    None,
                    {
                        **stylesheet,
                        **taxa_stylesheet
                    }
                ))

                ipca_ta_group.add_row()
                ipca_ta_group.add_cell(Cell(
                    ipca_ta_group,
                    self.inputs,
                    f'row_{i}',
                    {
                        'text': '=(1+@0)*(1+@1)-1',
                        'references': [
                            {
                                'path': ['taxa-emissao', f'ipca-anual-{tranche.id}', f'row_{i}'],
                                'static': False
                            },
                            {
                                'path': ['prelude', f'{tranche.id}-juros', layers_count - tranche_i],
                                'static': True
                            }
                        ]
                    },
                    {'taxa_text', 'taxa_percentage_2_0'},
                    None,
                    {
                        **stylesheet,
                        **taxa_stylesheet
                    }
                ))

                mensal_group.add_row()
                mensal_group.add_cell(Cell(
                    mensal_group,
                    self.inputs,
                    f'row_{i}',
                    {
                        'text': '=(1+@0)^(1/12)-1',
                        'references': [
                            {
                                'path': ['taxa-emissao', f'ipca-ta-{tranche.id}', f'row_{i}'],
                                'static': True
                            }
                        ]
                    },
                    {'taxa_text', 'taxa_percentage_4_0', 'e'},
                    None,
                    {
                        **stylesheet,
                        **taxa_stylesheet
                    }
                ))

            self.add_group(periodo_group)
            self.add_group(ipca_anual_group)
            self.add_group(ipca_ta_group)
            self.add_group(mensal_group)

            self.add_row()

            borders = {'w', 'e'}
            if tranche_i == layers_count - 1:
                borders.add('s')

            empty_group = EmptyGroup((1, 4), borders)
            self.add_group(empty_group)
