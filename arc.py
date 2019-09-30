import sys
import os

import pandas as pd
import numpy as np
import xlsxwriter

import json

import time
import locale

import re

# INPUTS AND SANITATION

inputs = json.loads(sys.stdin.readlines()[0])

saldo_files = inputs['inputFiles']
output_path = inputs['outputFile']
indexador = inputs['indexador']
pu_emis = inputs['pu-emis']
total = inputs['total']
r_sen = inputs['r-sen']
r_sub = inputs['r-sub']
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

col_width = 30
row_format = lambda x, y: '{0:<{2}} | {1:<{2}}'.format('{:,.2f} R$'.format(x),
                                                       '{:,.2f} R$'.format(y),
                                                       col_width)
def print_data():
    print('{0:^{2}} | {1:^{2}}'.format('SEN', 'SUB', col_width))

    for i, m in enumerate(months):
        if i >= len(saldo_sen_evol):
            break

        print('\n{0:^{1}}'.format(m, 2 * col_width + 3))

        print('{} : Saldo'.format(row_format(saldo_sen_evol[i],
                                             saldo_sub_evol[i])))

        print('{} : Juros'.format(row_format(juros_sen_evol[i],
                                             juros_sub_evol[i])))

        print('{} : Amort.'.format(row_format(amort_sen_evol[i],
                                              amort_sub_evol[i])))

        print('{} : PMT'.format(row_format(pmt_sen_evol[i],
                                           pmt_sub_evol[i])))

        print('{0:<{2}} | {1:<{2}} : Amort. %'\
              .format('{:,.4f}%'.format(amort_perc_sen_evol[i]),
                      '{:,.4f}%'.format(amort_perc_sub_evol[i]),
                      col_width))

transition_rows = []
while True:
    current_layer = 0
    transition_rows = []

    if len(mesostrata):
        _, r_current_layer, t_em_anual_current_layer = mesostrata[current_layer]
        t_em_mensal_current_layer = (1 + t_em_anual_current_layer) ** (1/12) - 1

        saldo_sub = total * r_current_layer / 100

        sub_phase_started = False
    else:
        saldo_sub = total * r_sub / 100
        juros_sub = saldo_sub * t_em_mensal
        sub_phase_started = True

    saldo_sen = total * r_sen / 100

    saldo_sen_evol                = []
    juros_sen_evol                = []
    amort_sen_evol                = []
    pmt_sen_evol                  = []
    amort_perc_sen_evol           = []

    saldo_sub_evol                = []
    despesas_sub_evol             = []
    juros_sub_evol                = []
    amort_sub_evol                = []
    pmt_sub_evol                  = []
    amort_perc_sub_evol           = []

    sen_finished = False
    sub_finished = False

    sen_length = 0
    sub_length = 0

    for m in range(len(months)):
        pmt_adjustment = 0
        if sub_finished:
            pmt_adjustment = pmt_sub_evol[-1]
            if len(mesostrata):
                current_layer += 1
                if current_layer < len(mesostrata):
                    t_em_mensal_current_layer = (1 + t_em_anual_current_layer) ** (1/12) - 1
                    saldo_sub = total * r_current_layer / 100
                    _, r_current_layer, t_em_anual_current_layer = mesostrata[current_layer]
                elif sub_phase_started:
                    break
                else:
                    saldo_sub = total * r_sub / 100
                    sub_phase_started = True
                sub_finished = False
            else:
                break
            transition_rows.append(m)

        if current_layer < len(mesostrata):
            juros_sub = saldo_sub * t_em_mensal_current_layer / 100
        else:
            juros_sub = saldo_sub * t_em_mensal

        sub_length += 1

        if not sen_finished:
            amort_sub = 0

            juros_sen = saldo_sen * t_em_senior_mensal
            sen_length += 1

            if m > c_period - 1:
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

            pmt_sub = flux_total[m - 1] * pmt_proper - pmt_adjustment
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

    inv_flux = [-total, *np.zeros(c_period)] + [sum(x) for x in list(zip(amort_sub_evol,
                                                                         juros_sub_evol,
                                                                         amort_sen_evol,
                                                                         juros_sen_evol))[c_period:]]

    irr = ((1 + np.irr(inv_flux)) ** 12 - 1) * 100

    if not sub_finished:
        pmt_proper = int((pmt_proper + .01) * 100) / 100
    else:
        if abs(target_irr - irr) > .004:
            t_em_anual *= ((target_irr / irr) ** (1 / (len(mesostrata) + 1))) * (1 - np.random.randint(5) / 100)
            t_em_mensal = (1 + t_em_anual) ** (1/12) - 1
        else:
            break

print_data()

# OUTPUT

workbook = xlsxwriter.Workbook(output_path)
workbook.set_size(1400, 1000)
curve_sheet = workbook.add_worksheet()
curve_sheet.hide_gridlines(2)

curve_sheet.insert_image('F2', '{}/logos-logo.png'.format(os.path.dirname(os.path.abspath(__file__))), {'x_scale': 0.75, 'y_scale': 0.85, 'x_offset': 10, 'y_offset': -10})

column_widths = [6, 18, 15.5, 14, 17.5, 19, 12, 13.5, 8, 6, 11, 8, 4, 6, 8, 13, 10, 12, 12, 11, 10, 4, 6, 8, 13, 10, 12, 12, 11, 4, 6, 6, 12]
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

# END SECTION

# SUBORDINATE TRANCHE

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

for i, saldo in list(enumerate(saldo_sub_evol)):
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

    if i == len(saldo_sub_evol) - 1:
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

    if i < len(saldo_sub_evol) - 1:
        if i >= c_period:
            a_val = '=T{0}-R{0}-Q{0}'.format(current_row)

            if saldo_sen_evol[i] > 0:
                pmt_val = '=Q{0}+R{0}'.format(current_row)
            elif saldo_sen_evol[i - 1] > 0:
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

# END SECTION

# SENIOR TRANCHE

l_border_format = workbook.add_format({'left': 1})
r_border_format = workbook.add_format({'right': 1})

def patch_border(is_l, row, col, n):
    for i in range(n):
        if is_l:
            curve_sheet.write(row + i, col, '', l_border_format)
        else:
            curve_sheet.write(row + i, col, '', r_border_format)

patch_border(True, 4, 13, 3)
patch_border(False, 4, 20, 1)
patch_border(False, 6, 20, 2)

curve_sheet.merge_range('W3:AC4', 'Tranche Sênior', section_title_format)
col_headers = ['Saldo Devedor', 'Juros', 'Amortiz', 'PMT', '% AM']

is_finished = False

for i, saldo in enumerate(saldo_sen_evol):
    prev_row = i + sub_y_offset
    current_row = prev_row + 1

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
        s_val = '=Y{0}+Z{1}-AB{1}'.format(prev_row, current_row)
        j_val = '=Y{}*C23'.format(prev_row)

        if i - sub_y_init_offset >= c_period:
            if saldo_sen_evol[i - sub_y_offset - 2] != 0:
                a_val = '=AB{0}-Z{0}'.format(current_row)
                pmt_val = '=K{}*H18-T{}'.format(i + sub_y_offset - 3, current_row)
            else:
                a_val = '=Y{}'.format(prev_row)
                pmt_val = '=Z{0}+AA{0}'.format(current_row)

                n_index_format.set_bottom(1)
                date_format.set_bottom(1)
                quantity_format.set_bottom(1)
                percentage_format.set_bottom(1)

                is_finished = True
        else:
            a_val = 0
            pmt_val = 0

        p_val = '=AA{}/Y{}'.format(current_row, prev_row)
    elif i == sub_y_init_offset - 1:
        i_val = i - sub_y_init_offset + 2
        m_val = m_bound
        s_val = saldo_sen

    curve_sheet.write(prev_row, 22, i_val, n_index_format)
    curve_sheet.write(prev_row, 23, m_val, date_format)
    curve_sheet.write(prev_row, 24, s_val, quantity_format)
    curve_sheet.write(prev_row, 25, j_val, quantity_format)
    curve_sheet.write(prev_row, 26, a_val, quantity_format)
    curve_sheet.write(prev_row, 27, pmt_val, quantity_format)
    curve_sheet.write(prev_row, 28, p_val, percentage_format)

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

            curve_sheet.write(prev_row, j + 24, h, col_header_format)

    if is_finished:
        break

# END SECTION

# FINANCIAL FLUX
curve_sheet.merge_range('AE3:AG4', 'Fluxo Financeiro', section_title_format)

currency_format_template = {
    'font_name': 'arial',
    'font_size': 9,
    'num_format': '_-* #,##0.00_-;-* #,##0.00_-;_-* "-"??_-;_-@_-',
    'right': 1
}

n_index_format = workbook.add_format(n_index_format_template)
date_format = workbook.add_format(date_format_template)
currency_format = workbook.add_format(currency_format_template)

curve_sheet.write(4, 30, 1, n_index_format)
curve_sheet.write(4, 31, m_bound, date_format)
curve_sheet.write(4, 32, -total, currency_format)

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

    curve_sheet.write(i + flux_y_offset, 30, i + 2, n_index_format)
    curve_sheet.write(i + flux_y_offset, 31, m, date_format)

    c_val = ''
    if i < c_period:
        c_val = 0
    else:
        c_val = '=R{0}+S{0}+Z{0}+AA{0}'.format(i + flux_y_offset + 4)
    curve_sheet.write(i + flux_y_offset, 32, c_val, currency_format)

    curve_sheet.set_row(i + flux_y_offset, 18)

# END SECTION

workbook.close()
