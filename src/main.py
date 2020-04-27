import session
import flux
import parse_input

import time
import locale

import numpy as np

import spreadsheet as ss

print('Processing inputs.')

inputs = parse_input.Input()

flux = flux.Flux(inputs.saldo_files, inputs.starting_date)
flux_total = flux.collapse()

taxa_juros_sub = .01

print('Inputs processed.\n')

print('Calculating curve.')

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

    print(irr)

curve = sess

print('Curve calculated.\n')

print('--- CURVE ---')
for tranche in curve.tranche_list:
    print('\n', tranche.title)
    for i, row in enumerate(tranche.row_list):
        print(i + 1, row.saldo, row.juros, row.amort, row.pmt)
print('--- END ---\n')

print('Rendering curve.')
spreadsheet = ss.Spreadsheet(
    inputs,
    flux_total,
    flux.months,
    taxa_juros_sub,
    (taxa_juros_sub + 1) ** 12 - 1,
    curve.tranche_list,
    len(curve.tranche_list[0].row_list),
    len(curve.tranche_list[-1].row_list),
    fluxo_financeiro,
)
spreadsheet.render_prelude()
spreadsheet.render_fluxo_creditos()
spreadsheet.resize_columns()
spreadsheet.render_file()

print('Curve rendered.')