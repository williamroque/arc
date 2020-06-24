from curva.framework.spreadsheet.section import Section
from curva.spreadsheet.util.empty_group import EmptyGroup
from curva.spreadsheet.prelude.group import PreludeGroup

import copy


class PreludeSection(Section):
    def __init__(self, parent_sheet, inputs):
        super().__init__(
            parent_sheet,
            inputs,
            'prelude',
            [0, 1],
            [11, 1]
        )

        layers_count = self.inputs.get('mezanine-layers-count') + 2

        self.add_row()

        total_group = PreludeGroup(
            self,
            self.inputs,
            'Valor Total',
            [
                {
                    'text': '={}'.format(self.inputs.get('total'))
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
                    'repeat': self.inputs.get('mezanine-layers-count')
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
                    'repeat': [self.inputs.get('pu-emis')] * layers_count
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
                    'repeat': [self.inputs.get('indexador')] * layers_count
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
                    'text': '={}'.format(self.inputs.get('taxas-juros-anual')['sen'])
                },
                {
                    'text': '={item}',
                    'repeat': self.inputs.get('taxas-juros-anual')['mezanino']
                },
                {
                    'text': '={}'.format(self.inputs.get('taxas-juros-anual')['sub'])
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
                    'text': '={}'.format(self.inputs.get('razoes')['sen'])
                },
                {
                    'text': '={item}',
                    'repeat': self.inputs.get('razoes')['mezanino']
                },
                {
                    'text': '={}'.format(self.inputs.get('razoes')['sub'])
                }
            ],
            set(['prelude_percentage_0']),
            'razoes',
            15.5
        )
        self.add_group(razoes_group)

        pu_liquidacao_group = PreludeGroup(
            self,
            self.inputs,
            'PU Liquidação',
            [
                {
                    'text': '={item}',
                    'repeat': [self.inputs.get('pu-emis')] * layers_count
                }
            ],
            set(['prelude_currency']),
            'pu-liquidacao',
            14
        )
        self.add_group(pu_liquidacao_group)

        quantidades_group = PreludeGroup(
            self,
            self.inputs,
            'Quantidades',
            [
                {
                    'text': '=@1/@0',
                    'repeat': layers_count,
                    'references': [
                        {
                            'path': ['prelude', 'pu-liquidacao'],
                            'static': True
                        },
                        {
                            'path': ['prelude', 'montante'],
                            'static': True
                        }
                    ]
                }
            ],
            set(['prelude_quantity']),
            'quantidades'
        )
        self.add_group(quantidades_group)

        montante_group = PreludeGroup(
            self,
            self.inputs,
            'Montante',
            [
                {
                    'text': '=@0*@1',
                    'repeat': layers_count,
                    'references': [
                        {
                            'path': ['prelude', 'valor-total'],
                            'static': True
                        },
                        {
                            'path': ['prelude', 'razoes'],
                            'static': True
                        }
                    ]
                }
            ],
            set(['prelude_currency']),
            'montante'
        )
        self.add_group(montante_group)

        prazo_group = PreludeGroup(
            self,
            self.inputs,
            'Prazo',
            [
                {
                    'text': '={}'.format(self.inputs.get('sen-length'))
                },
                {
                    'text': '={item}',
                    'repeat': self.inputs.get('mez-lengths')
                },
                {
                    'text': '={}'.format(self.inputs.get('sub-length'))
                }
            ],
            set(['prelude_text']),
            'prazo'
        )
        self.add_group(prazo_group)

        pmt_proper_group = PreludeGroup(
            self,
            self.inputs,
            '% PMT',
            [
                {
                    'text': self.inputs.get('pmt-proper')
                }
            ],
            set(['prelude_percentage_0']),
            'pmt-proper'
        )
        self.add_group(pmt_proper_group)

        self.add_row()

        periodo_group = PreludeGroup(
            self,
            self.inputs,
            'Período',
            [
                {
                    'text': 'Mensal'
                },
                {
                    'text': 'Anual'
                }
            ],
            set(['prelude_text']),
            'periodo'
        )
        self.add_group(periodo_group)

        senior_juros_group = PreludeGroup(
            self,
            self.inputs,
            'Sênior',
            [
                {
                    'text': self.inputs.get('taxas-juros')['sen'],
                },
                {
                    'text': '=(@0+1)^12-1',
                    'references': [
                        {
                            'path': ['prelude', 'senior-juros', 0],
                            'static': True
                        }
                    ],
                    'format': set(['prelude_percentage_2'])
                }
            ],
            set(['prelude_percentage_4']),
            'senior-juros'
        )
        self.add_group(senior_juros_group)

        for i, taxa in enumerate(self.inputs.get('taxas-juros')['mezanino']):
            group_id = f'mezanino-{i}-juros'
            mezanine_juros_group = PreludeGroup(
                self,
                self.inputs,
                'Mezanino',
                [
                    {
                        'text': taxa
                    },
                    {
                        'text': '=(@0+1)^12-1',
                        'references': [
                            {
                                'path': ['prelude', group_id, 0],
                                'static': True
                            }
                        ],
                        'format': set(['prelude_percentage_2'])
                    }
                ],
                set(['prelude_percentage_4']),
                group_id
            )
            self.add_group(mezanine_juros_group)

        subordinado_juros_group = PreludeGroup(
            self,
            self.inputs,
            'Subordinado',
            [
                {
                    'text': self.inputs.get('taxas-juros')['sub'],
                },
                {
                    'text': '=(@0+1)^12-1',
                    'references': [
                        {
                            'path': ['prelude', 'subordinado-juros', 0],
                            'static': True
                        }
                    ],
                    'format': set(['prelude_percentage_2'])
                }
            ],
            set(['prelude_percentage_4']),
            'subordinado-juros'
        )
        self.add_group(subordinado_juros_group)

        self.add_group(empty_group)  # IRR -> create fluxo financeiro first

        self.add_group(empty_group)  # FR 3 PMTs -> create tranches first

        fr_previsto_group = PreludeGroup(
            self,
            self.inputs,
            'FR Previsto',
            [
                {
                    'text': self.inputs.get('fr-previsto')
                }
            ],
            set(['prelude_currency']),
            'fr-previsto'
        )
        self.add_group(fr_previsto_group)


"""
[6, 18, 15.5, 14, 17.5, 19, 12, 13.5, 8, 6,
    11, 8, 4, 6, 8, 13, 10, 12, 12, 11, 10, 4]
[6, 8, 13, 12, 12, 11, 10, 4]
[6, 14, 8]
"""
