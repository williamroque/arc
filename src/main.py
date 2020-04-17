import session
import flux
import parse_input

import time
import locale

import numpy as np


inputs = parse_input.Input()

flux = flux.Flux(inputs.saldo_files, inputs.starting_date)
flux_total = flux.collapse()

taxa_juros_sub = .01

irr = None
while not irr or abs(inputs.target_irr - irr) >= .005:
    if irr:
        taxa_juros_sub *= inputs.target_irr / irr

    sess = session.Session(
        inputs.c_period,
        inputs.total,
        inputs.razoes,
        [taxa_juros_sub, *inputs.taxas_juros],
        inputs.pmt_proper,
        inputs.despesas,
        flux_total
    )
    sess.run()

    fluxo_financeiro = sess.collapse_financial_flux()
    irr = ((1 + np.irr(fluxo_financeiro)) ** 12 - 1) * 100
