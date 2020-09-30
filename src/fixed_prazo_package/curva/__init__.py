import time
import locale

import os
import json

import numpy as np

from curva.calculate.session import Session

from curva.util.flux import Flux
from curva.util.input import Input

from curva.spreadsheet.curve_sheet import CurveSheet


locale.setlocale(locale.LC_TIME, 'pt_BR')


def main():
    print('Processing inputs.', flush=True)

    inputs = Input()
    inputs.apply_map(
        'taxas-juros-anual',
        'taxas-juros',
        lambda x: (x + 1) ** (1/12) - 1
    )

    original_date = inputs.get('starting-date')

    inputs.update(
        'starting-date',
        time.strptime(inputs.get('starting-date'), '%b/%Y')
    )

    months, flux_total = Flux(
        inputs.get('planilhas-saldo'),
        inputs.get('starting-date')
    ).get_flux()

    inputs.update('flux-total', flux_total)
    inputs.update('flux-months', months)

    inputs.update('sub-pmt-proper', inputs.get('pmt-proper'))

    if 'mezanino' in inputs.get('razoes'):
        inputs.update(
            'mezanine-layers-count',
            len(inputs.get('razoes')['mezanino'])
        )
    else:
        inputs.update('mezanine-layers-count', 0)

    print('Inputs processed.\n', flush=True)


    print('Calculating curve.', flush=True)

    if inputs.get('taxas-juros-anual')['sub'] == -1:
        taxa_juros_sub = .01
        negative_baseline = 0

        irr = None
        while True:
            if irr:
                if irr < 0:
                    negative_baseline = taxa_juros_sub

                taxa_juros_sub *= inputs.get('target-irr') / abs(irr) ** (abs(irr) / irr)
                taxa_juros_sub += negative_baseline

            taxas_juros = inputs.get('taxas-juros')
            taxas_juros['sub'] = taxa_juros_sub
            inputs.update('taxas-juros', taxas_juros)

            taxas_juros_anual = inputs.get('taxas-juros-anual')
            taxas_juros_anual['sub'] = (taxa_juros_sub + 1) ** 12 - 1
            inputs.update('taxas-juros-anual', taxas_juros_anual)

            sess = Session(inputs)
            sess.run()

            fluxo_financeiro = sess.collapse_financial_flux()
            irr = (1 + np.irr(fluxo_financeiro)) ** 12 - 1

            if all([len(tranche.row_list) == inputs.get('target-prazos')[i] for i, tranche in enumerate(sess.tranche_list)]):
                if abs(inputs.get('target-irr') - irr) < .00005:
                    break
            else:
                sen_prazo = len(sess.tranche_list[1].row_list)
                target_sen_prazo = inputs.get('target-prazos')[1]

                sub_prazo = len(sess.tranche_list[0].row_list)
                target_sub_prazo = inputs.get('target-prazos')[0]

                if sen_prazo != target_sen_prazo:
                    print('sen_prazo', sen_prazo, flush=True)
                    pmt_proper = inputs.get('pmt-proper')
                    pmt_proper *= sen_prazo / target_sen_prazo
                    inputs.update('pmt-proper', pmt_proper)
                    inputs.update('sub-pmt-proper', pmt_proper)
                elif sub_prazo != target_sub_prazo:
                    print('sub_prazo', sub_prazo, flush=True)
                    sub_pmt_proper = inputs.get('sub-pmt-proper')
                    sub_pmt_proper *= np.sqrt(sub_prazo / target_sub_prazo)
                    print('proper', sub_pmt_proper, flush=True)
                    inputs.update('sub-pmt-proper', sub_pmt_proper)
    else:
        sess = Session(inputs)
        sess.run()

    inputs.update('tranche-list', sess.tranche_list)
    inputs.update('sub-length', len(sess.tranche_list[0].row_list)),
    inputs.update(
        'mez-lengths',
        [len(tranche.row_list) for tranche in sess.tranche_list[1:-1]]
    )
    inputs.update('sen-length', len(sess.tranche_list[-1].row_list))

    print('Curve calculated.\n', flush=True)


    print('--- CURVE ---', flush=True)

    for tranche in sess.tranche_list:
        print(tranche.title.center(26, '-'))
        for row in tranche.row_list:
            print(' '.join(map(str, row.get_values())))
        print()

    print('--- END ---\n', flush=True)


    print('Rendering curve.', flush=True)

    sheet = CurveSheet(inputs)
    sheet.render()

    print('Curve rendered.\n', flush=True)


    print('Saving curve data.', flush=True)

    inputs.update(
        'starting-date',
        original_date
    )

    file_name = os.path.splitext(inputs.get('output-path'))[0]
    path = file_name + '.curve'
    with open(path, 'w') as f:
        inputs.update('amort-percentages', {})
        inputs.update('atual', {})

        tranche_list = inputs.get('tranche-list')
        for i, tranche in enumerate(tranche_list):
            amort_percentages = list(map(
                lambda row: row.get_value('amort_perc'),
                tranche.row_list
            ))
            inputs.get('amort-percentages')[tranche.id] = amort_percentages
            inputs.get('atual')[inputs.get('primeira-serie') + i] = []

        inputs.update('tranche-list', None)
        f.write(json.dumps(inputs.inputs))

    print('Curve data saved.', flush=True)
