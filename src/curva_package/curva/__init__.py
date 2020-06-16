import time
import locale

import numpy as np

from curva.calculate.session import Session

from curva.util.flux import Flux
from curva.util.parse_input import Input

from curva.spreadsheet.curve_sheet import CurveSheet


def main():
    print('Processing inputs.')

    inputs = Input()

    flux = Flux(inputs.saldo_files, inputs.starting_date)
    flux_total = flux.collapse()

    print('Inputs processed.\n')


    print('Calculating curve.')

    taxa_juros_sub = .01

    irr = None
    while not irr or abs(inputs.target_irr - irr) >= .005:
        if irr:
            taxa_juros_sub *= inputs.target_irr / irr

        sess = Session(
            inputs.c_period,
            inputs.total,
            inputs.razoes,
            {
                'sub': taxa_juros_sub,
                **inputs.taxas_juros
            },
            inputs.pmt_proper,
            inputs.despesas,
            flux_total
        )
        sess.run()

        fluxo_financeiro = sess.collapse_financial_flux()
        irr = ((1 + np.irr(fluxo_financeiro)) ** 12 - 1) * 100

        print(irr)

    print('Curve calculated.\n')


    print('--- CURVE ---')

    for tranche in sess.tranche_list:
        print('\n', tranche.title)
        for i, row in enumerate(tranche.row_list):
            print(i + 1, row.saldo, row.juros, row.amort, row.pmt)

    print('--- END ---\n')


    print('Rendering curve.')

    sheet = CurveSheet(
        inputs,
        flux_total,
        flux.months,
        taxa_juros_sub,
        (taxa_juros_sub + 1) ** 12 - 1,
        sess.tranche_list,
        len(sess.tranche_list[0].row_list),
        [len(sess.tranche_list[i + 1].row_list) for i in range(len(inputs.razoes['mezanino']))],
        len(sess.tranche_list[-1].row_list),
        fluxo_financeiro
    )
    sheet.render()

    print('Curve rendered.')

