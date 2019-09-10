import sys
import pandas as pd
import numpy as np

import time
import locale

import re

total, r_sub, r_sen, t_em_anual, t_em_senior_anual, g_period, pmt_proper, despesas, *saldo_files = sys.argv[1:]

total = float(total)
r_sub = float(r_sub)
r_sen = float(r_sen)
t_em_anual = float(t_em_anual)
t_em_senior_anual = float(t_em_senior_anual)
g_period = float(g_period)
pmt_proper = float(pmt_proper) / 100
despesas = float(despesas)

t_em_anual /= 100
t_em_senior_anual /= 100

t_em_mensal = (1 + t_em_anual) ** (1/12) - 1
t_em_senior_mensal = (1 + t_em_senior_anual) ** (1/12) - 1

locale.setlocale(locale.LC_TIME, 'pt_BR')
re_date = re.compile('^\s*[A-Z][a-z]{2}/\d{4}\s*$')

def parse_frame(df):
    h, w = df.shape

    evolution = []
    for col in range(w):
        if re_date.match(df.iloc[0, col]):
            month = df.iloc[0, col]
            parsed_month = time.strptime(month, '%b/%Y')

            if not parsed_month < time.localtime():
                evolution.append((
                    month,
                    df.iloc[h - 1, col]
                ))

    return evolution

fluxo = {}
for file in saldo_files:
    df = pd.read_excel(file)
    parsed_df = parse_frame(df)
    for m in parsed_df:
        date, val = m
        if date in fluxo:
            fluxo[date].append(val)
        else:
            fluxo[date] = [val]

flux_total = [sum(fluxo[m]) for m in fluxo]
months = [m for m in fluxo]

nz_index = flux_total.index(next(i for i in flux_total if i != 0))
flux_total = flux_total[nz_index:]
months = months[nz_index:]

for i in range(len(flux_total) - 1, -1, -1):
    if flux_total[i] == 0:
        flux_total.pop()
        months.pop()
    else:
        break

saldo_sub = total * r_sub / 100
saldo_sen = total * r_sen / 100

saldo_sub_evol      = []
despesas_sub_evol   = []
juros_sub_evol      = []
amort_sub_evol      = []
pmt_sub_evol        = []
amort_perc_sub_evol = []

saldo_sen_evol      = []
juros_sen_evol      = []
amort_sen_evol      = []
pmt_sen_evol        = []
amort_perc_sen_evol = []

sub_finished = False
sen_finished = False

while True:
    for m in range(len(months)):
        if sub_finished:
            break

        juros_sub = saldo_sub * t_em_mensal

        if not sen_finished:
            amort_sub = 0

            juros_sen = saldo_sen * t_em_senior_mensal

            if m > g_period - 1:
                pmt_sub = juros_sub + despesas
                pmt_sen = flux_total[m - 1] * pmt_proper - pmt_sub
                amort_sen = pmt_sen - juros_sen
                amort_perc_sen = amort_sen / saldo_sen

                if amort_sen < 0:
                    break
            else:
                pmt_sub = pmt_sen = amort_sen = amort_perc_sen = 0

            saldo_sen = saldo_sen + juros_sen - pmt_sen
        else:
            juros_sen = pmt_sen = amort_sen = saldo_sen = 0

            pmt_sub = flux_total[m - 1] * pmt_proper
            amort_sub = pmt_sub - juros_sub - despesas

        amort_perc_sub = amort_sub / saldo_sub

        if amort_perc_sen >= 1 and not sen_finished:
            amort_sen = saldo_sen_evol[-1]
            pmt_sen = amort_sen + juros_sen

            pmt_sub = flux_total[m - 1] * pmt_proper - pmt_sen
            amort_sub = pmt_sub - juros_sub - despesas

            amort_perc_sub = amort_sub / saldo_sub

            sen_finished = True

        if amort_perc_sub >= 1:
            amort_sub = saldo_sub_evol[-1]
            pmt_sub = amort_sub + juros_sub + despesas
            sub_finished = True

        saldo_sub = saldo_sub + despesas + juros_sub - pmt_sub

        saldo_sub_evol.append(max(0, saldo_sub))
        despesas_sub_evol.append(despesas)
        juros_sub_evol.append(juros_sub)
        amort_sub_evol.append(amort_sub)
        pmt_sub_evol.append(pmt_sub)
        amort_perc_sub_evol.append(min(100, amort_perc_sub * 100))

        saldo_sen_evol.append(max(0, saldo_sen))
        juros_sen_evol.append(juros_sen)
        amort_sen_evol.append(amort_sen)
        pmt_sen_evol.append(pmt_sen)
        amort_perc_sen_evol.append(min(100, amort_perc_sen * 100))

    if not sub_finished:
        saldo_sub = total * r_sub / 100
        saldo_sen = total * r_sen / 100

        saldo_sub_evol      = []
        despesas_sub_evol   = []
        juros_sub_evol      = []
        amort_sub_evol      = []
        pmt_sub_evol        = []
        amort_perc_sub_evol = []

        saldo_sen_evol      = []
        juros_sen_evol      = []
        amort_sen_evol      = []
        pmt_sen_evol        = []
        amort_perc_sen_evol = []

        sub_finished = False
        sen_finished = False

        pmt_proper = int((pmt_proper + .01) * 100) / 100
    else:
        break

def print_data():
    for i, m in enumerate(months):
        if i >= len(saldo_sen_evol):
            break

        print(f'\n--- {m} ---')
        print('SUB')
        print('Saldo', saldo_sub_evol[i])
        print('Despesas', despesas_sub_evol[i])
        print('Juros', juros_sub_evol[i])
        print('Amort.', amort_sub_evol[i])
        print('PMT', pmt_sub_evol[i])
        print('Amort. %', amort_perc_sub_evol[i])

        print('\nSEN')
        print('Saldo', saldo_sen_evol[i])
        print('Juros', juros_sen_evol[i])
        print('Amort.', amort_sen_evol[i])
        print('PMT', pmt_sen_evol[i])
        print('Amort. %', amort_perc_sen_evol[i])

print_data()
