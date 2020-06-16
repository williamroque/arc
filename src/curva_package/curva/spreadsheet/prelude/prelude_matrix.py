def create_matrix(inputs, taxas_juros_sub, taxas_juros_anual_sub, sub_length, mez_lengths, sen_length):
    mezanine_layers_count = len(inputs.razoes['mezanino'])
    return [
        [
            {
                'title': 'Valor Total',
                'body': [
                    '=' + str(inputs.total)
                ],
                'format': ['prelude_currency']
            },
            {},
            {},
            {
                'title': 'Série',
                'body': [
                    'Sênior',
                    *['Mezanino' for _ in range(mezanine_layers_count)],
                    'Subordinado'
                ],
                'format': ['prelude_text']
            },
            {
                'title': 'PU Emissão',
                'body': [
                    '=' + str(inputs.pu_emis),
                    *['=' + str(inputs.pu_emis) for _ in range(mezanine_layers_count)],
                    '=' + str(inputs.pu_emis)
                ],
                'format': ['prelude_currency']
            },
            {
                'title': 'Indexador',
                'body': [
                    '=' + str(inputs.indexador),
                    *['=' + str(inputs.indexador) for _ in range(mezanine_layers_count)],
                    '=' + str(inputs.indexador)
                ],
                'format': ['prelude_text']
            },
            {
                'title': 'Taxa de Juros',
                'body': [
                    '=' + str(inputs.taxas_juros_anual['sen']),
                    *['=' + str(taxa) for taxa in inputs.taxas_juros_anual['mezanino']],
                    '=' + str(taxas_juros_anual_sub)
                ],
                'format': ['prelude_percentage_2']
            }
        ],
        [
            {
                'title': 'Série',
                'body': [
                    'Sênior',
                    *['Mezanino' for _ in range(mezanine_layers_count)],
                    'Subordinado'
                ],
                'format': ['prelude_text']
            },
            {
                'title': 'Razão',
                'body': [
                    '=' + str(inputs.razoes['sen']),
                    *['=' + str(razao) for razao in inputs.razoes['mezanino']],
                    '=' + str(inputs.razoes['sub'])
                ],
                'format': ['prelude_percentage_0']
            },
            {
                'title': 'PU Liquidação',
                'body': [
                    '=' + str(inputs.pu_emis),
                    *['=' + str(inputs.pu_emis) for _ in range(mezanine_layers_count)],
                    '=' + str(inputs.pu_emis)
                ],
                'format': ['prelude_currency']
            },
            {
                'title': 'Quantidades',
                'body': [
                    '={i_next}/{i_prev}',
                    *['={i_next}/{i_prev}' for _ in range(mezanine_layers_count)],
                    '={i_next}/{i_prev}'
                ],
                'format': ['prelude_quantity']
            },
            {
                'title': 'Montante',
                'body': [
                    '={Valor_Total}*{Razão}',
                    *['={Valor_Total}*{Razão}' for _ in range(mezanine_layers_count)],
                    '={Valor_Total}*{Razão}'
                ],
                'format': ['prelude_currency']
            },
            {
                'title': 'Prazo',
                'body': [
                    '=' + str(sen_length),
                    *['=' + str(length) for length in mez_lengths],
                    '=' + str(sub_length)
                ],
                'format': ['prelude_text']
            },
            {
                'title': '% PMT',
                'body': [
                    '=' + str(inputs.pmt_proper)
                ],
                'format': ['prelude_percentage_0']
            }
        ],
        [
            {
                'title': 'Período',
                'body': [
                    'Mensal',
                    'Anual'
                ],
                'format': ['prelude_text']
            },
            {
                'title': 'Sênior',
                'body': [
                    '=' + str(inputs.taxas_juros['sen']),
                    '=({prev_body}+1)^12-1'
                ],
                'format': [
                    'prelude_percentage_4',
                    'prelude_percentage_2'
                ]
            },
            *[
                {
                    'title': 'Mezanino',
                    'body': [
                        '=' + str(taxa),
                        '=({prev_body}+1)^12-1'
                    ],
                    'format': [
                        'prelude_percentage_4',
                        'prelude_percentage_2'
                    ]
                } for taxa in inputs.taxas_juros['mezanino']
            ],
            {
                'title': 'Subordinado',
                'body': [
                    '=' + str(taxas_juros_sub),
                    '=({prev_body}+1)^12-1'
                ],
                'format': [
                    'prelude_percentage_4',
                    'prelude_percentage_2'
                ]
            },
            {
                'title': 'TIR',
                'body': [
                    '=IRR({fluxo_fin_start}:{fluxo_fin_end})',
                    '=(1+{prev_body})^12-1'
                ],
                'format': [
                    'prelude_percentage_2',
                    'prelude_percentage_2'
                ]
            },
            {
                'title': 'FR 3 PMTS',
                'body': [
                    '=SUM({fluxo_3_sum_terms})*{P_PMT}-SUM({despesas_3_sum_terms})'
                ],
                'format': [
                    'prelude_currency'
                ]
            },
            {
                'title': 'FR Previsto',
                'body': [
                    '=' + str(inputs.fr_previsto)
                ],
                'format': [
                    'prelude_currency'
                ]
            }
        ]
    ]
