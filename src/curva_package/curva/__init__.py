import time
import locale

import numpy as np

from curva.calculate.session import Session

from curva.util.flux import Flux
from curva.util.input import Input

from curva.spreadsheet.curve_sheet import CurveSheet


locale.setlocale(locale.LC_TIME, 'pt_BR')


def main():
    print('Processing inputs.')

    inputs = Input()
    inputs.apply_map(
        'taxas-juros-anual',
        'taxas-juros',
        lambda x: (x + 1) ** (1/12) - 1
    )

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

    if 'mezanino' in inputs.get('razoes'):
        inputs.update(
            'mezanine-layers-count',
            len(inputs.get('razoes')['mezanino'])
        )
    else:
        inputs.update('mezanine-layers-count', 0)

    print('Inputs processed.\n')


    print('Calculating curve.')

    taxa_juros_sub = .01
    negative_baseline = 0

    irr = None
    while not irr or abs(inputs.get('target-irr') - irr) >= .00005:
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
        irr = ((1 + np.irr(fluxo_financeiro)) ** 12 - 1)

    inputs.update('tranche-list', sess.tranche_list)
    inputs.update('sub-length', len(sess.tranche_list[0].row_list)),
    inputs.update(
        'mez-lengths',
        [len(tranche.row_list) for tranche in sess.tranche_list[1:-1]]
    )
    inputs.update('sen-length', len(sess.tranche_list[-1].row_list))

    print('Curve calculated.\n')


    print('--- CURVE ---')

    for tranche in sess.tranche_list:
        print('\n', tranche.title)
        for i, row in enumerate(tranche.row_list):
            print(i + 1, end=' ')
            for value in row.get_values():
                print(value, end=' ')
            print()

    print('--- END ---\n')


    print('Rendering curve.')

    sheet = CurveSheet(inputs)
    sheet.render()

    print('Curve rendered.')
