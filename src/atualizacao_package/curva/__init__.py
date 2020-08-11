import json
import locale
import time
import numpy as np
from scipy.optimize import minimize, Bounds

from curva.util.input import Input
from curva.util.flux import Flux

from curva.calculate.session import Session

locale.setlocale(locale.LC_TIME, 'pt_BR')


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
    def irr_at_distribution(distribution):
        for i, _ in enumerate(inputs.get('atual-amex')[str(primeira_serie)]):
            inputs.get('atual-amex')[str(primeira_serie)][i] = amex_total * distribution[i]
            inputs.get('atual-amex')[str(primeira_serie + 1)][i] = amex_total * (1 - distribution[i])

        sess = Session(inputs)
        sess.run()

        fluxo_financeiro = sess.collapse_financial_flux()
        irr = (1 + np.irr(fluxo_financeiro)) ** 12 - 1

        return abs(inputs.get('curve')['target-irr'] - irr)

    x_0 = np.ones(len(inputs.get('atual-amex')[str(primeira_serie)]))
    minimize(irr_at_distribution, x_0, method='Powell', bounds=Bounds(x_0 * 0, x_0))

    # Write own optimization function

    sess = Session(inputs)
    sess.run()
    fluxo_financeiro = sess.collapse_financial_flux()
    print((1 + np.irr(fluxo_financeiro)) ** 12 - 1)
    for tranche in sess.tranche_list:
        print(tranche.title)
        for row in tranche.row_list:
            print(list(map(lambda x: round(x, 2) if x != None else None, row.get_values())))
        print()


    print('Curve calculated.\n', flush=True)

    print('Rendering curve.', flush=True)
    print('Curve rendered.\n', flush=True)

    print('Saving curve data.', flush=True)
    print('Curve data saved.', flush=True)
