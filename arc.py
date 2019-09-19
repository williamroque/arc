import sys
import os

import pandas as pd
import numpy as np
import xlsxwriter

import json

import time
import locale

import re

import datetime

# INPUTS AND SANITATION

inputs = json.loads(sys.stdin.readlines()[0])

saldo_files = inputs['inputFiles']
output_path = inputs['outputFile']
indexador = inputs['indexador']
pu_emis = inputs['pu-emis']
total = inputs['total']
r_sen = inputs['r-sen']
r_sub = inputs['r-sub']

# (mesostrata = intermediary layers)
mesostrata = inputs['mesostrata']

target_irr = inputs['target-irr']
t_em_senior_anual = inputs['t-em-senior-anual']
c_period = inputs['c-period']
fr_previsto = inputs['fr-previsto']
pmt_proper = inputs['pmt-proper']
despesas = inputs['despesas']

total = float(total)
r_sen = float(r_sen)
r_sub = float(r_sub)
target_irr = float(target_irr)
t_em_senior_anual = float(t_em_senior_anual)
c_period = int(c_period)
pmt_proper = float(pmt_proper) / 100
despesas = float(despesas)

fr_previsto = int(fr_previsto)

t_em_anual = t_em_senior_anual

t_em_anual /= 100
t_em_senior_anual /= 100

t_em_mensal = (1 + t_em_anual) ** (1/12) - 1
t_em_senior_mensal = (1 + t_em_senior_anual) ** (1/12) - 1
t_em_mesostrata_mensal = [(1 + layer[2] / 100) ** (1/12) - 1 for layer in mesostrata]

locale.setlocale(locale.LC_TIME, 'pt_BR')
re_date = re.compile('^\s*[A-Z][a-z]{2}/\d{4}\s*$')

def parse_frame(df):
    h, w = df.shape

    evolution = []
    for col in range(w):
        if re_date.match(df.iloc[0, col]):
            month = df.iloc[0, col]
            parsed_month = time.strptime(month, '%b/%Y')
            now = time.localtime()

            p_y = parsed_month.tm_year
            p_m = parsed_month.tm_mon
            n_y = now.tm_year
            n_m = now.tm_mon

            if p_y > n_y or (p_y == n_y and p_m > n_m):
                pass
            elif p_y == n_y and p_m == n_m:
                pass
            else:
                continue

            evolution.append((
                time.strftime('%b-%y', parsed_month),
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

m_bound = months[0]
f_bound = flux_total[0]

months = months[1:]
flux_total = flux_total[1:]

nz_index = flux_total.index(next(i for i in flux_total if i != 0))
flux_total = flux_total[nz_index:]

months = months[nz_index:]

for i in range(len(flux_total) - 1, -1, -1):
    if flux_total[i] == 0:
        flux_total.pop()
        months.pop()
    else:
        break

# CURVE CALCULATION

while True:
    dynamic_despesas = despesas

    saldo_sen             = total * r_sen / 100
    saldo_sen_evol        = []
    pmt_sen_evol          = []
    amort_sen_evol        = []
    juros_sen_evol        = []

    saldo_mesostrata      = [total * layer[1] / 100 for layer in mesostrata]
    saldo_mesostrata_evol = [[] for _ in mesostrata]
    pmt_mesostrata_evol   = [[] for _ in mesostrata]
    amort_mesostrata_evol = [[] for _ in mesostrata]
    juros_mesostrata_evol = [[] for _ in mesostrata]

    saldo_sub             = total * r_sub / 100
    saldo_sub_evol        = []
    pmt_sub_evol          = []
    amort_sub_evol        = []
    juros_sub_evol        = []

    current_layer = 0
    is_transitioning = False

    sen_finished = False

    sen_length = 0
    sub_length = 0

    for i, m in enumerate(months):
        juros_sub = saldo_sub * t_em_mensal
        juros_mesostrata = [saldo_mesostrata[layer_i] * t_em_mesostrata_mensal[layer_i] for layer_i, layer in enumerate(mesostrata)]
        juros_sen = saldo_sen * t_em_senior_mensal

        if i > c_period - 1:
            pmt_sub = juros_sub + dynamic_despesas
            pmt_mesostrata = juros_mesostrata.copy()
            pmt_sen = flux_total[i - 1] * pmt_proper - sum(pmt_mesostrata) - pmt_sub

            if current_layer == len(mesostrata) + 1:
                if is_transitioning:
                    if len(mesostrata):
                        pmt_sub = flux_total[i - 1] * pmt_proper - pmt_mesostrata[0]
                    else:
                        pmt_sub = flux_total[i - 1] * pmt_proper - pmt_sen
                    is_transitioning = False
                else:
                    pmt_sub = flux_total[i - 1] * pmt_proper
            elif current_layer >= 1:
                if is_transitioning:
                    pmt_mesostrata[-current_layer] = flux_total[i - 1] * pmt_proper - (pmt_sen if current_layer == 1 else pmt_mesostrata[-current_layer - 1])
                    is_transitioning = False
                else:
                    pmt_mesostrata[-current_layer] = flux_total[i - 1] * pmt_proper

            amort_sub = pmt_sub - juros_sub - dynamic_despesas
            amort_mesostrata = [a - b for a, b in zip(pmt_mesostrata, juros_mesostrata)]
            amort_sen = pmt_sen - juros_sen
        else:
            pmt_sub = amort_sub = 0
            pmt_mesostrata = amort_mesostrata = [0 for _ in mesostrata]
            pmt_sen = amort_sen = 0

        if saldo_sub <= 0:
            break
        for layer_i, saldo_layer in enumerate(saldo_mesostrata):
            if saldo_layer <= 0:
                pmt_mesostrata[layer_i] = juros_mesostrata[layer_i] = amort_mesostrata[layer_i] = 0
        if saldo_sen <= 0:
            pmt_sen = juros_sen = amort_sen = 0
        print(i, m, saldo_sub, saldo_mesostrata, saldo_sen, pmt_sub, pmt_mesostrata, pmt_sen, juros_sub, juros_mesostrata, juros_sen, flux_total[i - 1])

        saldo_sub = saldo_sub + dynamic_despesas + juros_sub - pmt_sub
        saldo_mesostrata = [saldo_mesostrata[layer_i] + juros_mesostrata[layer_i] - pmt_mesostrata[layer_i] for layer_i, layer in enumerate(mesostrata)]
        saldo_sen = saldo_sen + juros_sen - pmt_sen

        saldo_sub_evol.append(saldo_sub)
        for layer_i, layer in enumerate(saldo_mesostrata_evol):
            layer.append(saldo_mesostrata[layer_i])
        saldo_sen_evol.append(saldo_sen)

        pmt_sub_evol.append(pmt_sub)
        for layer_i, layer in enumerate(pmt_mesostrata_evol):
            layer.append(pmt_mesostrata[layer_i])
        pmt_sen_evol.append(pmt_sen)

        amort_sub_evol.append(amort_sub)
        for layer_i, layer in enumerate(amort_mesostrata_evol):
            layer.append(amort_mesostrata[layer_i])
        amort_sen_evol.append(amort_sen)

        juros_sub_evol.append(juros_sub)
        for layer_i, layer in enumerate(juros_mesostrata_evol):
            layer.append(juros_mesostrata[layer_i])
        juros_sen_evol.append(juros_sen)

        if not current_layer == len(mesostrata) + 1:
            if current_layer == 0 and saldo_sen <= 0 or \
               current_layer >= 1 and saldo_mesostrata[-current_layer] <= 0:
                sen_finished = True
                is_transitioning = True
                current_layer += 1

        sub_length += 1
        if not sen_finished:
            sen_length += 1

    inv_flux = [-total, *np.zeros(c_period)]
    for i in range(len(amort_sub_evol)):
        inv_flux.append(amort_sub_evol[i] + juros_sub_evol[i] +
                        sum([layer[i] for layer in amort_mesostrata_evol]) + sum([layer[i] for layer in juros_mesostrata_evol]) +
                        amort_sen_evol[i] + juros_sen_evol[i])

    irr = ((1 + np.irr(inv_flux)) ** 12 - 1) * 100

    print('IRR -- PMT_PROPER -- TARGET_IRR / IRR -- T_EM_MENSAL')
    print( '------', irr, pmt_proper, target_irr / irr, t_em_anual, '------')

    if saldo_sub_evol[-1] > 0:
        pmt_proper += .01
    else:
        if abs(target_irr - irr) > .04:
            t_em_anual *= (target_irr / irr) ** (len(mesostrata) + 1)
            t_em_mensal = (1 + t_em_anual) ** (1/12) - 1
        else:
            break

# OUTPUT

workbook = xlsxwriter.Workbook(output_path)
workbook.set_size(1400, 1000)
curve_sheet = workbook.add_worksheet()
curve_sheet.hide_gridlines(2)

curve_sheet.insert_image('F2', '{}/logos-logo.png'.format(os.path.dirname(os.path.abspath(__file__))), {'x_scale': 0.75, 'y_scale': 0.85, 'x_offset': 10, 'y_offset': -10})

column_widths = [6, 18, 15.5, 14, 17.5, 19, 12, 13.5, 8, 6, 11, 8, 4, 6, 8, 13, 10, 12, 12, 11, 10, 4]
column_widths = column_widths + list(map(int, ('6 8 13 12 12 11 10 4 ' * (1 + len(mesostrata))).strip().split(' '))) + [6, 6, 12]

for i, w in enumerate(column_widths):
    curve_sheet.set_column(i, i, w)

# GENERAL STYLING SECTION

prelude_header_format = workbook.add_format({
    'bold': True,
    'font_color': 'white',
    'font_name': 'arial',
    'font_size': 9,
    'align': 'center',
    'valign': 'vcenter',
    'border': 2,
    'border_color': 'white',
    'bg_color': '#3465FC'
})

prelude_text_format = workbook.add_format({
    'font_name': 'arial',
    'font_size': 9,
    'align': 'center',
    'valign': 'vcenter'
})

prelude_percentage_0_format = workbook.add_format({
    'font_name': 'arial',
    'font_size': 9,
    'align': 'center',
    'valign': 'vcenter',
    'num_format': '0%'
})

prelude_percentage_2_format = workbook.add_format({
    'font_name': 'arial',
    'font_size': 9,
    'align': 'center',
    'valign': 'vcenter',
    'num_format': '0.00%'
})

prelude_percentage_4_format = workbook.add_format({
    'font_name': 'arial',
    'font_size': 9,
    'align': 'center',
    'valign': 'vcenter',
    'num_format': '0.0000%'
})

prelude_quantity_format = workbook.add_format({
    'font_name': 'arial',
    'font_size': 9,
    'valign': 'vcenter',
    'num_format': '#,##0_);(#,##0)',
})

prelude_currency_format = workbook.add_format({
    'font_name': 'arial',
    'font_size': 9,
    'bold': True,
    'num_format': '_("R$"* #,##0.00_);_("R$"* (#,##0.00);_("R$"* "-"??_);_(@_)'
})

section_title_format = workbook.add_format({
    'bold': True,
    'italic': True,
    'font_color': '#477DC0',
    'font_name': 'arial',
    'font_size': 10,
    'align': 'center',
    'valign': 'vcenter',
    'top': 1,
    'left': 1,
    'right': 1
})

# END SECTION

# FLUXO

curve_sheet.merge_range('J3:L4', 'Fluxo de Créditos Imobiliários', section_title_format)

flux_y_offset = 5

n_index_format_template = {
    'align': 'center',
    'left': 1
}
flux_format_template = {
    'bold': True,
    'num_format': '#,##0.00',
    'align': 'left'
}
date_format_template = {
    'align': 'center',
    'right': 1
}

n_index_format = workbook.add_format(n_index_format_template)
flux_format = workbook.add_format(flux_format_template)
date_format = workbook.add_format(date_format_template)

curve_sheet.write(flux_y_offset - 1, 9, 1, n_index_format)
curve_sheet.write(flux_y_offset - 1, 10, f_bound, flux_format)
curve_sheet.write(flux_y_offset - 1, 11, m_bound, date_format)

for i, m in enumerate(months):
    n_index_format = workbook.add_format(n_index_format_template)
    flux_format = workbook.add_format(flux_format_template)
    date_format = workbook.add_format(date_format_template)

    if i == len(months) - 1:
        n_index_format.set_bottom(1)
        flux_format.set_bottom(1)
        date_format.set_bottom(1)

    curve_sheet.write(i + flux_y_offset, 9, i + 2, n_index_format)
    curve_sheet.write(i + flux_y_offset, 10, flux_total[i], flux_format)
    curve_sheet.write(i + flux_y_offset, 11, m, date_format)

    curve_sheet.set_row(i + flux_y_offset, 18)

# END SECTION

saldo_sub = total * r_sub / 100
saldo_sen = total * r_sen / 100

# PRELUDE SECTION

def write_prelude_section(x, y, title, values):
    curve_sheet.write(y, x, title, prelude_header_format)
    for i, (v, f) in enumerate(values):
        curve_sheet.write(y + i + 1, x, v, f)

write_prelude_section(1, 11, 'Taxa de Juros', [
    (target_irr / 100, prelude_percentage_2_format)
])
write_prelude_section(2, 11, 'Valor Total', [
    (total, prelude_currency_format)
])
write_prelude_section(4, 11, 'Série', [
    ('Sênior', prelude_text_format),
    ('Subordinado', prelude_text_format)
])
write_prelude_section(5, 11, 'PU Emissão', [
    (int(pu_emis), prelude_currency_format),
    (int(pu_emis), prelude_currency_format)
])
write_prelude_section(6, 11, 'Indexador', [
    (indexador, prelude_text_format),
    (indexador, prelude_text_format)
])
write_prelude_section(7, 11, 'Taxa de Juros', [
    (t_em_senior_anual, prelude_percentage_2_format),
    (t_em_anual, prelude_percentage_2_format),
])

# ROW

write_prelude_section(1, 16, 'Série', [
    ('Sênior', prelude_text_format),
    ('Subordinado', prelude_text_format)
])
write_prelude_section(2, 16, 'PU Liquidação', [
    (int(pu_emis), prelude_currency_format),
    (int(pu_emis), prelude_currency_format)
])
write_prelude_section(3, 16, 'Quantidades', [
    ('=E18/C18', prelude_quantity_format),
    ('=E19/C19', prelude_quantity_format)
])
write_prelude_section(4, 16, 'Montante', [
    ('=C13*G18', prelude_currency_format),
    ('=C13*G19', prelude_currency_format)
])
write_prelude_section(5, 16, 'Prazo', [
    ('{} meses'.format(sen_length), prelude_text_format),
    ('{} meses'.format(sub_length), prelude_text_format)
])
write_prelude_section(6, 16, 'Razão', [
    (r_sen / 100, prelude_percentage_0_format),
    (r_sub / 100, prelude_percentage_0_format)
])
write_prelude_section(7, 16, '% PMT', [
    (pmt_proper, prelude_percentage_0_format)
])

# ROW

write_prelude_section(1, 21, 'Período', [
    ('Mensal', prelude_text_format),
    ('Anual', prelude_text_format)
])
write_prelude_section(2, 21, 'Sênior', [
    ('=(1+C24)^(1/12)-1', prelude_percentage_4_format),
    (t_em_senior_anual, prelude_percentage_2_format)
])
write_prelude_section(3, 21, 'Subordinado', [
    ('=(1+D24)^(1/12)-1', prelude_percentage_4_format),
    (t_em_anual, prelude_percentage_2_format)
])
write_prelude_section(4, 21, 'TIR', [
    ('=IRR(AG{}:AG{})'.format(flux_y_offset, flux_y_offset + len(saldo_sub_evol)), prelude_percentage_2_format),
    ('=(1+E23)^12-1', prelude_percentage_2_format)
])

sub_y_offset = 3
sub_y_init_offset = 5

write_prelude_section(6, 21, 'FR 3 PMTS', [
    ('=SUM(K{}:K{})*H18-SUM(Q{}:Q{})'.format(flux_y_offset, flux_y_offset + c_period, sub_y_offset + sub_y_init_offset, sub_y_offset + sub_y_init_offset + c_period), prelude_currency_format)
])
write_prelude_section(7, 21, 'FR Previsto', [
    (fr_previsto, prelude_currency_format)
])

# ROW

write_prelude_section(1, 26, 'Período', [
    ('Mensal', prelude_text_format),
    ('Anual', prelude_text_format)
])

def get_relative_cell(c_r, c_c, d_r, d_c):
    return xlsxwriter.utility.xl_rowcol_to_cell(c_r + d_r, c_c + d_c)

for i, layer in enumerate(mesostrata):
    col = 7 - i
    write_prelude_section(col, 26, layer[0], [
        (
            '=(1+{})^(1/12)-1'.format(
                get_relative_cell(27, col, 1, 0)
            ),
             prelude_percentage_4_format
        ),
        (layer[2] / 100, prelude_percentage_2_format)
    ])

# END SECTION

# SUBORDINATE TRANCHE

l_border_format = workbook.add_format({'left': 1})
r_border_format = workbook.add_format({'right': 1})

def patch_border(is_l, row, col, n):
    for i in range(n):
        if is_l:
            curve_sheet.write(row + i, col, '', l_border_format)
        else:
            curve_sheet.write(row + i, col, '', r_border_format)

curve_sheet.merge_range('N3:U4', 'Tranche Subordinado', section_title_format)

col_headers = ['Saldo Devedor', 'Despesas', 'Juros', 'Amortiz', 'PMT', '% AM']

header_y_offset = 2

for i, h in enumerate(col_headers):
    col_header_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'font_size': 10,
        'font_name': 'arial'
    })
    if i == len(col_headers) - 1:
        col_header_format.set_right(1)

    curve_sheet.write(sub_y_offset + header_y_offset, i + 15, h, col_header_format)

n_index_format_template = {
    'font_name': 'arial',
    'font_size': 10,
    'align': 'center',
    'left': 1
}
date_format_template = {
    'font_name': 'arial',
    'font_size': 10,
    'align': 'center'
}
quantity_format_template = {
    'font_name': 'arial',
    'font_size': 10,
    'num_format': '_-* #,##0.00_-;-* #,##0.00_-;_-* "-"??_-;_-@_-'
}

n_index_format = workbook.add_format(n_index_format_template)
date_format = workbook.add_format(date_format_template)
quantity_format = workbook.add_format(quantity_format_template)

init_row = sub_y_offset + sub_y_init_offset - 1
curve_sheet.write(init_row, 13, 1, n_index_format)
curve_sheet.write(init_row, 14, m_bound, date_format)
curve_sheet.write(init_row, 15, saldo_sub, quantity_format)

patch_border(True, 3, 13, 4)
patch_border(False, 4, 20, 1)
patch_border(False, 6, 20, 2)

i = 0
while saldo_sub_evol[i + 2] > 0:
    prev_row = i + sub_y_offset + sub_y_init_offset
    current_row = prev_row + 1

    n_index_format = workbook.add_format(n_index_format_template)
    date_format = workbook.add_format(date_format_template)
    quantity_format = workbook.add_format(quantity_format_template)
    percentage_format = workbook.add_format({
        'font_name': 'arial',
        'font_size': 10,
        'align': 'center',
        'right': 1,
        'num_format': '0.0000%'
    })

    if saldo_sub_evol[i + 3] <= 0:
        n_index_format.set_bottom(1)
        date_format.set_bottom(1)
        quantity_format.set_bottom(1)
        percentage_format.set_bottom(1)

    i_val = m_val = s_val = d_val = j_val = a_val = pmt_val = p_val = ''

    i_val = i + 2
    m_val = months[i]
    s_val = '=P{0}+Q{1}+R{1}-T{1}'.format(prev_row, current_row)
    d_val = despesas
    j_val = '=P{}*D23'.format(prev_row)

    if saldo_sub_evol[i + 3] > 0:
        if i >= c_period:
            a_val = '=T{0}-R{0}-Q{0}'.format(current_row)

            if saldo_mesostrata_evol[0][i + 1] > 0:
                pmt_val = '=Q{0}+R{0}'.format(current_row)
            elif saldo_mesostrata_evol[0][i] > 0:
                pmt_val = '=K{}*H18-AB{}'.format(i + sub_y_offset + sub_y_init_offset - 3, current_row)
            else:
                pmt_val = '=K{}*H18'.format(i + sub_y_offset + sub_y_init_offset - 3)
        else:
            a_val = pmt_val = 0
    else:
        a_val = '=P{}'.format(prev_row)
        pmt_val = '=Q{0}+R{0}+S{0}'.format(current_row)

    p_val = '=S{}/P{}'.format(current_row, prev_row)

    curve_sheet.write(prev_row, 13, i_val, n_index_format)
    curve_sheet.write(prev_row, 14, m_val, date_format)
    curve_sheet.write(prev_row, 15, s_val, quantity_format)
    curve_sheet.write(prev_row, 16, d_val, quantity_format)
    curve_sheet.write(prev_row, 17, j_val, quantity_format)
    curve_sheet.write(prev_row, 18, a_val, quantity_format)
    curve_sheet.write(prev_row, 19, pmt_val, quantity_format)
    curve_sheet.write(prev_row, 20, p_val, percentage_format)

    i += 1

# END SECTION

# INTERMEDIARY TRANCHES

initial_column_position = 22
tranche_width = 7
for layer_i, layer in enumerate(mesostrata):
    column_base_position = initial_column_position + layer_i * tranche_width + layer_i
    curve_sheet.merge_range(2, column_base_position, 3,  column_base_position + tranche_width - 1, layer[0], section_title_format)

    col_headers = ['Saldo Devedor', 'Juros', 'Amortiz', 'PMT', '% AM']

    header_y_offset = 2

    for i, h in enumerate(col_headers):
        col_header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 10,
            'font_name': 'arial'
        })
        if i == len(col_headers) - 1:
            col_header_format.set_right(1)

        curve_sheet.write(sub_y_offset + header_y_offset, i + column_base_position + 2, h, col_header_format)

    n_index_format_template = {
        'font_name': 'arial',
        'font_size': 10,
        'align': 'center',
        'left': 1
    }
    date_format_template = {
        'font_name': 'arial',
        'font_size': 10,
        'align': 'center'
    }
    quantity_format_template = {
        'font_name': 'arial',
        'font_size': 10,
        'num_format': '_-* #,##0.00_-;-* #,##0.00_-;_-* "-"??_-;_-@_-'
    }

    n_index_format = workbook.add_format(n_index_format_template)
    date_format = workbook.add_format(date_format_template)
    quantity_format = workbook.add_format(quantity_format_template)

    init_row = sub_y_offset + sub_y_init_offset - 1
    curve_sheet.write(init_row, column_base_position, 1, n_index_format)
    curve_sheet.write(init_row, column_base_position + 1, m_bound, date_format)
    curve_sheet.write(init_row, column_base_position + 2, total * layer[1] / 100, quantity_format)

    patch_border(True, 3, column_base_position, 4)
    patch_border(False, 4, column_base_position + tranche_width - 1, 1)
    patch_border(False, 6, column_base_position + tranche_width - 1, 2)

    i = 0
    while saldo_mesostrata_evol[layer_i][max(i, 0)] > 0:
        current_row = i + sub_y_offset + sub_y_init_offset

        n_index_format = workbook.add_format(n_index_format_template)
        date_format = workbook.add_format(date_format_template)
        quantity_format = workbook.add_format(quantity_format_template)
        percentage_format = workbook.add_format({
            'font_name': 'arial',
            'font_size': 10,
            'align': 'center',
            'right': 1,
            'num_format': '0.0000%'
        })

        if saldo_mesostrata_evol[layer_i][i + 1] <= 0:
            n_index_format.set_bottom(1)
            date_format.set_bottom(1)
            quantity_format.set_bottom(1)
            percentage_format.set_bottom(1)

        i_val = m_val = s_val = j_val = a_val = pmt_val = p_val = ''

        i_val = i + 2
        m_val = months[i]

        saldo_col = column_base_position + 2
        prev_saldo_cell = get_relative_cell(current_row, saldo_col, -1, 0)
        s_val = '={}+{}-{}'.format(
            prev_saldo_cell,
            get_relative_cell(current_row, saldo_col, 0, 1),
            get_relative_cell(current_row, saldo_col, 0, 3)
        )
        j_val = '={}*{}'.format(prev_saldo_cell, get_relative_cell(27, 7 - layer_i, 0, 0))

        if saldo_mesostrata_evol[layer_i][i + 1] > 0:
            if i >= c_period:
                a_val = '={}-{}'.format(
                    get_relative_cell(current_row, saldo_col, 0, 3),
                    get_relative_cell(current_row, saldo_col, 0, 1)
                )

                if saldo_sen_evol[i] > 0:
                    pmt_val = '={}'.format(
                        get_relative_cell(current_row, saldo_col, 0, 1)
                    )
                elif saldo_sen_evol[i - 1] > 0:
                    pmt_val = '=K{}*H18-{}'.format(
                        current_row,
                        get_relative_cell(current_row, saldo_col + 3, 0, tranche_width)
                    )
                else:
                    pmt_val = '=K{}*H18'.format(current_row)
            else:
                a_val = pmt_val = 0
        else:
            a_val = '={}'.format(prev_saldo_cell)
            pmt_val = '={}+{}'.format(
                get_relative_cell(current_row, saldo_col, 0, 1),
                get_relative_cell(current_row, saldo_col, 0, 2)
            )

        p_val = '={}/{}'.format(
            get_relative_cell(current_row, saldo_col, 0, 2),
            prev_saldo_cell
        )

        curve_sheet.write(current_row, column_base_position, i_val, n_index_format)
        curve_sheet.write(current_row, column_base_position + 1, m_val, date_format)
        curve_sheet.write(current_row, column_base_position + 2, s_val, quantity_format)
        curve_sheet.write(current_row, column_base_position + 3, j_val, quantity_format)
        curve_sheet.write(current_row, column_base_position + 4, a_val, quantity_format)
        curve_sheet.write(current_row, column_base_position + 5, pmt_val, quantity_format)
        curve_sheet.write(current_row, column_base_position + 6, p_val, percentage_format)

        i += 1

ultimate_intermediary_offset = tranche_width * len(mesostrata) + initial_column_position + len(mesostrata)

# END SECTION

# SENIOR TRANCHE

curve_sheet.merge_range(2, ultimate_intermediary_offset, 3, ultimate_intermediary_offset + tranche_width - 1, 'Tranche Sênior', section_title_format)
col_headers = ['Saldo Devedor', 'Juros', 'Amortiz', 'PMT', '% AM']

is_finished = False

for i, saldo in enumerate(saldo_sen_evol):
    current_row = i + sub_y_offset

    n_index_format = workbook.add_format({
        'font_name': 'arial',
        'font_size': 10,
        'align': 'center',
        'left': 1
    })
    date_format = workbook.add_format({
        'font_name': 'arial',
        'font_size': 10,
        'align': 'center'
    })
    quantity_format = workbook.add_format({
        'font_name': 'arial',
        'font_size': 10,
        'num_format': '_-* #,##0.00_-;-* #,##0.00_-;_-* "-"??_-;_-@_-'
    })
    percentage_format = workbook.add_format({
        'font_name': 'arial',
        'font_size': 10,
        'align': 'center',
        'right': 1,
        'num_format': '0.0000%'
    })

    i_val = m_val = s_val = j_val = a_val = pmt_val = p_val = ''

    if i >= sub_y_init_offset:
        i_val = i - sub_y_init_offset + 2
        m_val = months[i - sub_y_init_offset]

        saldo_col = ultimate_intermediary_offset + 2
        prev_saldo_cell = get_relative_cell(current_row, saldo_col, -1, 0)
        s_val = '={}+{}-{}'.format(
            prev_saldo_cell,
            get_relative_cell(current_row, saldo_col, 0, 1),
            get_relative_cell(current_row, saldo_col, 0, 3)
        )
        j_val = '={}*C23'.format(prev_saldo_cell)

        if i - sub_y_init_offset >= c_period:
            if saldo_sen_evol[i - sub_y_offset - 2] > 0:
                a_val = '={}-{}'.format(
                    get_relative_cell(current_row, saldo_col + 2, 0, 1),
                    get_relative_cell(current_row, saldo_col + 2, 0, -1)
                )
                mesostrata_pmts = '-'.join([get_relative_cell(current_row, saldo_col - (tranche_width + 1) * i, 0, -5) for i in range(len(mesostrata))])
                pmt_val = '=K{}*H18-{}-T{}'.format(
                    i + sub_y_offset - 3,
                    mesostrata_pmts,
                    current_row + 1
                )
            else:
                a_val = '={}'.format(get_relative_cell(current_row, saldo_col, -1, 0))
                pmt_val = '={}+{}'.format(
                    get_relative_cell(current_row, saldo_col + 3, 0, -1),
                    get_relative_cell(current_row, saldo_col + 3, 0, -2)
                )

                n_index_format.set_bottom(1)
                date_format.set_bottom(1)
                quantity_format.set_bottom(1)
                percentage_format.set_bottom(1)

                is_finished = True
        else:
            a_val = 0
            pmt_val = 0

        p_val = '={}/{}'.format(
            get_relative_cell(current_row, saldo_col + 2, 0, 0),
            get_relative_cell(current_row, saldo_col, -1, 0)
        )
    elif i == sub_y_init_offset - 1:
        i_val = i - sub_y_init_offset + 2
        m_val = m_bound
        s_val = saldo_sen

    curve_sheet.write(current_row, ultimate_intermediary_offset, i_val, n_index_format)
    curve_sheet.write(current_row, ultimate_intermediary_offset + 1, m_val, date_format)
    curve_sheet.write(current_row, ultimate_intermediary_offset + 2, s_val, quantity_format)
    curve_sheet.write(current_row, ultimate_intermediary_offset + 3, j_val, quantity_format)
    curve_sheet.write(current_row, ultimate_intermediary_offset + 4, a_val, quantity_format)
    curve_sheet.write(current_row, ultimate_intermediary_offset + 5, pmt_val, quantity_format)
    curve_sheet.write(current_row, ultimate_intermediary_offset + 6, p_val, percentage_format)

    if i == header_y_offset:
        for j, h in enumerate(col_headers):
            col_header_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'font_size': 10,
                'font_name': 'arial'
            })
            if j == len(col_headers) - 1:
                col_header_format.set_right(1)

            curve_sheet.write(current_row, j + ultimate_intermediary_offset + 2, h, col_header_format)

    if is_finished:
        break

# END SECTION

# FINANCIAL FLUX
curve_sheet.merge_range(2, ultimate_intermediary_offset + tranche_width + 1, 3, ultimate_intermediary_offset + tranche_width + 3, 'Fluxo Financeiro', section_title_format)

currency_format_template = {
    'font_name': 'arial',
    'font_size': 9,
    'num_format': '_-* #,##0.00_-;-* #,##0.00_-;_-* "-"??_-;_-@_-',
    'right': 1
}

n_index_format = workbook.add_format(n_index_format_template)
date_format = workbook.add_format(date_format_template)
currency_format = workbook.add_format(currency_format_template)

curve_sheet.write(4, ultimate_intermediary_offset + tranche_width + 1, 1, n_index_format)
curve_sheet.write(4, ultimate_intermediary_offset + tranche_width + 2, m_bound, date_format)
curve_sheet.write(4, ultimate_intermediary_offset + tranche_width + 3, -total, currency_format)

for i, m in enumerate(months):
    if i >= len(saldo_sub_evol):
        break

    n_index_format = workbook.add_format(n_index_format_template)
    date_format = workbook.add_format(date_format_template)
    currency_format = workbook.add_format(currency_format_template)

    if i == len(saldo_sub_evol) - 1:
        n_index_format.set_bottom(1)
        date_format.set_bottom(1)
        currency_format.set_bottom(1)

    curve_sheet.write(i + flux_y_offset, ultimate_intermediary_offset + tranche_width + 1, i + 2, n_index_format)
    curve_sheet.write(i + flux_y_offset, ultimate_intermediary_offset + tranche_width + 2, m, date_format)

    c_val = ''
    if i < c_period:
        c_val = 0
    else:
        current_row = i + flux_y_offset + 3
        c_val = '=R{0}+S{0}'.format(current_row + 1)
        c_val += '+'.join([''] + [get_relative_cell(current_row, ultimate_intermediary_offset + 3 - (tranche_width + 1) * i, 0, 0) for i in range(len(mesostrata) + 1)])
        c_val += '+'.join([''] + [get_relative_cell(current_row, ultimate_intermediary_offset + 3 - (tranche_width + 1) * i, 0, 1) for i in range(len(mesostrata) + 1)])
    curve_sheet.write(i + flux_y_offset, ultimate_intermediary_offset + tranche_width + 3, c_val, currency_format)

    curve_sheet.set_row(i + flux_y_offset, 18)

# END SECTION

workbook.close()
