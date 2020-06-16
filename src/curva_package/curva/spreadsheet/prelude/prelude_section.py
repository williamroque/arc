from curva.framework.spreadsheet.section import Section
from curva.spreadsheet.prelude.prelude_group import PreludeGroup
from curva.spreadsheet.empty_group import EmptyGroup

import copy


class PreludeSection(Section):
    def __init__(self, parent_sheet, inputs, taxas_juros_anual_sub, taxa_juros_sub):
        super().__init__(
            parent_sheet,
            inputs,
            'prelude-section',
            [0, 1],
            [11, 1],
            False
        )

        if 'mezanino' in self.inputs.razoes:
            mezanine_layers_count = len(self.inputs.razoes['mezanino'])
        else:
            mezanine_layers_count = 0

        layers_count = mezanine_layers_count + 2

        self.add_row()

        total_group = PreludeGroup(
            self,
            self.inputs,
            'Valor Total',
            [
                {
                    'text': '={}'.format(self.inputs.total)
                }
            ],
            set(['prelude_currency']),
            'valor-total',
            18
        )
        self.add_group(total_group)

        empty_group = EmptyGroup()
        self.add_group(empty_group)
        self.add_group(empty_group)

        series_label_group = PreludeGroup(
            self,
            self.inputs,
            'Série',
            [
                {
                    'text': 'Sênior'
                },
                {
                    'text': 'Mezanino',
                    'repeat': mezanine_layers_count
                },
                {
                    'text': 'Subordinado'
                }
            ],
            set(['prelude_text']),
            '',
            17.5
        )
        self.add_group(series_label_group)

        pu_emis_group = PreludeGroup(
            self,
            self.inputs,
            'PU Emissão',
            [
                {
                    'text': '={item}',
                    'repeat': [self.inputs.pu_emis] * layers_count
                }
            ],
            set(['prelude_currency']),
            'pu-emis',
            19
        )
        self.add_group(pu_emis_group)

        indexador_group = PreludeGroup(
            self,
            self.inputs,
            'Indexador',
            [
                {
                    'text': '={item}',
                    'repeat': [self.inputs.indexador] * layers_count
                }
            ],
            set(['prelude_text']),
            'indexador',
            12
        )
        self.add_group(indexador_group)

        taxas_juros_group = PreludeGroup(
            self,
            self.inputs,
            'Taxa de Juros',
            [
                {
                    'text': '={}'.format(inputs.taxas_juros_anual['sen'])
                },
                {
                    'text': '={item}',
                    'repeat': self.inputs.taxas_juros_anual['mezanino']
                },
                {
                    'text': '={}'.format(taxas_juros_anual_sub)
                }
            ],
            set(['prelude_percentage_2']),
            'taxas-juros',
            13.5
        )
        self.add_group(taxas_juros_group)

        self.add_row()

        self.add_group(copy.deepcopy(series_label_group))

        razoes_group = PreludeGroup(
            self,
            self.inputs,
            'Razão',
            [
                {
                    'text': '={}'.format(self.inputs.razoes['sen'])
                },
                {
                    'text': '={item}',
                    'repeat': self.inputs.razoes['mezanino']
                },
                {
                    'text': '={}'.format(self.inputs.razoes['sub'])
                }
            ],
            set(['prelude_percentage_0']),
            'razoes',
            15.5
        )
        self.add_group(razoes_group)

"""
[6, 18, 15.5, 14, 17.5, 19, 12, 13.5, 8, 6, 11, 8, 4, 6, 8, 13, 10, 12, 12, 11, 10, 4]
[6, 8, 13, 12, 12, 11, 10, 4]
[6, 14, 8]
"""
