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

        layers_count = self.inputs.get('curve')['mezanine-layers-count'] + 2

        self.add_row()

        total_group = PreludeGroup(
            self,
            self.inputs,
            'Valor Total',
            [
                {
                    'text': '={}'.format(self.inputs.get('curve')['total'])
                }
            ],
            set(['prelude_currency']),
            'valor-total',
            18
        )
        self.add_group(total_group)

        empty_group = EmptyGroup()
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
                    'repeat': self.inputs.get('curve')['mezanine-layers-count']
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

        taxas_juros_group = PreludeGroup(
            self,
            self.inputs,
            'Taxa de Juros',
            [
                {
                    'text': '={}'.format(self.inputs.get('curve')['taxas-juros-anual']['sen'])
                },
                {
                    'text': '={item}',
                    'repeat': self.inputs.get('curve')['taxas-juros-anual']['mezanino'] if 'mezanino' in self.inputs.get('curve')['taxas-juros-anual'] else 0
                },
                {
                    'text': '={}'.format(self.inputs.get('curve')['taxas-juros-anual']['sub'])
                }
            ],
            set(['prelude_percentage_2']),
            'taxas-juros',
            13.5
        )
        self.add_group(taxas_juros_group)

        razoes_group = PreludeGroup(
            self,
            self.inputs,
            'Razão',
            [
                {
                    'text': '={}'.format(self.inputs.get('curve')['razoes']['sen'])
                },
                {
                    'text': '={item}',
                    'repeat': self.inputs.get('curve')['razoes']['mezanino'] if 'mezanino' in self.inputs.get('curve')['razoes'] else 0
                },
                {
                    'text': '={}'.format(self.inputs.get('curve')['razoes']['sub'])
                }
            ],
            set(['prelude_percentage_0']),
            'razoes',
            15.5
        )
        self.add_group(razoes_group)

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
            'montante',
            17.5
        )
        self.add_group(montante_group)

        prazo_group = PreludeGroup(
            self,
            self.inputs,
            'Prazo',
            [
                {
                    'text': '=@{index}',
                    'repeat': self.inputs.get('tranche-list'),
                    'references': [
                        {
                            'path': [tranche.id, 'n', f'row_{len(tranche.row_list) - 1}'],
                            'static': True
                        } for tranche in self.inputs.get('tranche-list')[::-1]
                    ]
                }
            ],
            set(['prelude_text']),
            'prazo',
            12
        )
        self.add_group(prazo_group)

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
                    'text': '=(@0+1)^(1/12)-1',
                    'references': [
                        {
                            'path': ['prelude', 'senior-juros', 1],
                            'static': True
                        }
                    ]
                },
                {
                    'text': '=@0',
                    'references': [
                        {
                            'path': ['prelude', 'taxas-juros', 0],
                            'static': True
                        }
                    ],
                    'format': set(['prelude_percentage_2'])
                }
            ],
            set(['prelude_percentage_4']),
            'senior-juros',
            17.5
        )
        self.add_group(senior_juros_group)

        if 'mezanino' in self.inputs.get('curve')['taxas-juros']:
            for i, taxa in enumerate(self.inputs.get('curve')['taxas-juros']['mezanino']):
                group_id = f'mezanino-{i}-juros'
                mezanine_juros_group = PreludeGroup(
                    self,
                    self.inputs,
                    'Mezanino',
                    [
                        {
                            'text': '=(@0+1)^(1/12)-1',
                            'references': [
                                {
                                    'path': ['prelude', group_id, 1],
                                    'static': True
                                }
                            ]
                        },
                        {
                            'text': '=@0',
                            'references': [
                                {
                                    'path': ['prelude', 'taxas-juros', layers_count - i - 1],
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
                    'text': '=(@0+1)^(1/12)-1',
                    'references': [
                        {
                            'path': ['prelude', 'subordinado-juros', 1],
                            'static': True
                        }
                    ]
                },
                {
                    'text': '=@0',
                    'references': [
                        {
                            'path': ['prelude', 'taxas-juros', layers_count - 1],
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

        tranche_list = self.inputs.get('tranche-list')
        max_tranche_length = max(
            [len(tranche.row_list) for tranche in tranche_list]
        )
        irr_group = PreludeGroup(
            self,
            self.inputs,
            'TIR',
            [
                {
                    'text': '=IRR(@0:@1)',
                    'references': [
                        {
                            'path': ['fluxo-financeiro', 'value', 'total'],
                            'static': True
                        },
                        {
                            'path': ['fluxo-financeiro', 'value', f'row_{max_tranche_length - 1}'],
                            'static': True
                        }
                    ]
                },
                {
                    'text': '=(1+@0)^12-1',
                    'references': [
                        {
                            'path': ['prelude', 'irr', 0],
                            'static': True
                        }
                    ]
                }
            ],
            set(['prelude_percentage_2']),
            'irr'
        )
        self.add_group(irr_group)

        fr_3_pmts_group = PreludeGroup(
            self,
            self.inputs,
            'FR 3 PMTs',
            [
                {
                    'text': '=SUM(@0:@1)-SUM(@2:@3)',
                    'references': [
                        {
                            'path': ['fluxo-creditos', 'value', 'row_0'],
                            'static': True
                        },
                        {
                            'path': ['fluxo-creditos', 'value', 'row_2'],
                            'static': True
                        },
                        {
                            'path': ['subordinado', 'despesas', 'row_1'],
                            'static': True
                        },
                        {
                            'path': ['subordinado', 'despesas', 'row_3'],
                            'static': True
                        },
                    ]
                }
            ],
            set(['prelude_currency']),
            'fr-3-pmts'
        )
        self.add_group(fr_3_pmts_group)

        fr_previsto_group = PreludeGroup(
            self,
            self.inputs,
            'FR Previsto',
            [
                {
                    'text': self.inputs.get('curve')['fr-previsto']
                }
            ],
            set(['prelude_currency']),
            'fr-previsto'
        )
        self.add_group(fr_previsto_group)

