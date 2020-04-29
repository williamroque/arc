
curve_sheet.merge_range('J3:L4', 'Fluxo de Créditos Imobiliários', section_title_format)

flux_y_offset = 5


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

def get_relative_cell(c_r, c_c, d_r, d_c):
    return xlsxwriter.utility.xl_rowcol_to_cell(c_r + d_r, c_c + d_c)

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

tranche_width = 7
financial_flux_column = 25 + tranche_width * (len(mesostrata) + 1) + len(mesostrata)
write_prelude_section(4, 21, 'TIR', [
    ('=IRR({}:{})'.format(get_relative_cell(flux_y_offset - 1, financial_flux_column, 0, 0),
                          get_relative_cell(flux_y_offset - 1, financial_flux_column, len(saldo_sub_evol), 0)), prelude_percentage_2_format),
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

for i, layer in enumerate(mesostrata):
    write_prelude_section(i + 2, 26, layer[0], [
        (
            '=(1+{})^(1/12)-1'.format(
                get_relative_cell(27, i + 2, 1, 0)
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
    col_header_format = workbook.add_format()
    if i == len(col_headers) - 1:
        col_header_format.set_right(1)

    curve_sheet.write(sub_y_offset + header_y_offset, i + 15, h, col_header_format)

n_index_format_template = 
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

            if len(mesostrata) and saldo_mesostrata_evol[0][i + 1] > 0 or saldo_sen_evol[i - 2] > 0 and not len(mesostrata):
                pmt_val = '=Q{0}+R{0}'.format(current_row)
            elif len(mesostrata) and saldo_mesostrata_evol[0][i] > 0 or saldo_sen_evol[i - 3] > 0 and not len(mesostrata):
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
        j_val = '={}*{}'.format(prev_saldo_cell, get_relative_cell(27, layer_i + 2, 0, 0))

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
                pmt_val = '=K{}*H18{}-T{}'.format(
                    i + sub_y_offset - 3,
                    '-{}'.format(mesostrata_pmts) if len(mesostrata) else '',
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

