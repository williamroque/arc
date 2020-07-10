import json
import locale
import time
import numpy as np

from curva.util.input import Input
from curva.util.flux import Flux

locale.setlocale(locale.LC_TIME, 'pt_BR')


def main():
    print('Processing inputs.', flush=True)

    inputs = Input()

    with open(inputs.get('arquivo-curva')) as f:
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

    historical_period = 0
    for serie in inputs.get('curve')['atual'].keys():
        if serie in inputs.get('atual-juros'):
            for i, taxa_juros in enumerate(inputs.get('atual-juros')[serie]):
                inputs.get('curve')['atual'][serie].append([
                    taxa_juros,
                    inputs.get('atual-amort')[serie][i],
                    inputs.get('atual-amex')[serie][i]
                ])
            if i + 1 > historical_period:
                historical_period = i + 1
    inputs.update('historical_period', historical_period)

    print('Inputs processed.\n', flush=True)

    print('Calculating curve.', flush=True)

    irr = None
    while not irr or abs(inputs.get('curve')['target-irr'] - irr) >= .00005:
        if irr:
            pass
            

        sess = Session(inputs)
        sess.run()

        fluxo_financeiro = sess.collapse_financial_flux()
        irr = (1 + np.irr(fluxo_financeiro)) ** 12 - 1

    print('Curve calculated.\n', flush=True)

    print('Rendering curve.', flush=True)
    print('Curve rendered.\n', flush=True)

    print('Saving curve data.', flush=True)
    print('Curve data saved.', flush=True)
