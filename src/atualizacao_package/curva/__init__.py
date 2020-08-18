import json
import locale
import time
import numpy as np

from curva.util.input import Input
from curva.util.flux import Flux
from curva.calculate.session import Session
from curva.spreadsheet.curve_sheet import CurveSheet

locale.setlocale(locale.LC_TIME, 'pt_BR')


def minimize(func, bounds=(0, 1), step=.05):
    f_0 = func(bounds[0])
    f_1 = func(bounds[1])

    if f_0 < f_1:
        x = bounds[0]
        y = f_0
    else:
        x = bounds[1]
        y = f_1

        step = -step

    while (f_x := func(x + step)) < y:
        x += step
        y = f_x

    return x


def main():
    print('Processing inputs.', flush=True)

    inputs = Input()

    with open(inputs.get('arquivo-curva')[0]) as f:
        inputs.update('curve', json.loads(f.read()))

    original_date = inputs.get('curve')['starting-date']
    inputs.update(
        'starting-date',
        time.strptime(inputs.get('curve')['starting-date'], '%b/%Y')
    )

    months, flux_total = Flux(
        inputs.get('curve')['planilhas-saldo'],
        inputs.get('starting-date')
    ).get_flux()

    inputs.update('flux-total', flux_total)
    inputs.update('flux-months', months)

    atual = inputs.get('curve')['atual']
    for serie in inputs.get('curve')['atual'].keys():
        if serie in inputs.get('atual-juros'):
            i = -1
            for i, atual_row in enumerate(atual[serie][::-1]):
                inputs.get('atual-juros')[serie] = atual_row[0] + inputs.get('atual-juros')
                inputs.get('atual-amort')[serie] = atual_row[1] + inputs.get('atual-amort')
                inputs.get('atual-amex')[serie] = atual_row[2] + inputs.get('atual-amex')
                inputs.get('atual-pu')[serie] = atual_row[3] + inputs.get('atual-pu')
                inputs.get('atual-quantidade')[serie] = atual_row[4] + inputs.get('atual-quantidade')
    inputs.update('historical-period', len(inputs.get('atual-juros')[serie]))

    print('Inputs processed.\n', flush=True)

    print('Calculating curve.', flush=True)

    sess = None

    primeira_serie = inputs.get('curve')['primeira-serie']

    amex_total = sum([row[-1] for row in inputs.get('atual-amex').values()])
    def irr_at_distribution(perc_sen):
        inputs.get('atual-amex')[str(primeira_serie)][-1] = amex_total * perc_sen
        inputs.get('atual-amex')[str(primeira_serie + 1)][-1] = amex_total * (1 - perc_sen)

        sess = Session(inputs)
        sess.run()

        fluxo_financeiro = sess.collapse_financial_flux()
        irr = (1 + np.irr(fluxo_financeiro)) ** 12 - 1

        return abs(inputs.get('curve')['target-irr'] - irr)

    print('Optimized distribution:', minimize(irr_at_distribution), flush=True)

    sess = Session(inputs)
    sess.run()
    fluxo_financeiro = sess.collapse_financial_flux()

    inputs.update('tranche-list', sess.tranche_list)

    print('--- CURVE ---', flush=True)

    for tranche in sess.tranche_list:
        print(tranche.title.center(26, '-'))
        for row in tranche.row_list:
            print(' '.join(map(str, row.get_values())))
        print()

    print('--- END ---\n', flush=True)

    irr = (1 + np.irr(fluxo_financeiro)) ** 12 - 1
    print('IRR:', f'{irr * 100}%', f'({round(irr * 100, 2)}%)', flush=True)

    print('Curve calculated.\n', flush=True)

    print('Rendering curve.', flush=True)

    sheet = CurveSheet(inputs)
    sheet.render()

    print('Curve rendered.\n', flush=True)

    print('Saving curve data.', flush=True)
    print('Curve data saved.', flush=True)
