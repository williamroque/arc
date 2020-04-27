formats = {}

formats['prelude_header'] = {
    'is_template': False,
    'format': {
        'bold': True,
        'font_color': 'white',
        'font_name': 'arial',
        'font_size': 9,
        'align': 'center',
        'valign': 'vcenter',
        'border': 2,
        'border_color': 'white',
        'bg_color': '#3465FC'
    }
}

formats['prelude_text'] = {
    'is_template': False,
    'format': {
        'font_name': 'arial',
        'font_size': 9,
        'align': 'center',
        'valign': 'vcenter'
    }
}

formats['prelude_percentage_0'] = {
    'is_template': False,
    'format': {
        'font_name': 'arial',
        'font_size': 9,
        'align': 'center',
        'valign': 'vcenter',
        'num_format': '0%'
    }
}

formats['prelude_percentage_2'] = {
    'is_template': False,
    'format': {
        'font_name': 'arial',
        'font_size': 9,
        'align': 'center',
        'valign': 'vcenter',
        'num_format': '0.00%'
    }
}

formats['prelude_percentage_4'] = {
    'is_template': False,
    'format': {
        'font_name': 'arial',
        'font_size': 9,
        'align': 'center',
        'valign': 'vcenter',
        'num_format': '0.0000%'
    }
}

formats['prelude_quantity'] = {
    'is_template': False,
    'format': {
        'font_name': 'arial',
        'font_size': 9,
        'valign': 'vcenter',
        'num_format': '#,##0_);(#,##0)',
    }
}

formats['prelude_currency'] = {
    'is_template': False,
    'format': {
        'font_name': 'arial',
        'font_size': 9,
        'bold': True,
        'num_format': '_("R$"* #,##0.00_);_("R$"* (#,##0.00);_("R$"* "-"??_);_(@_)'
    }
}

formats['section_title'] = {
    'is_template': False,
    'format': {
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
    }
}

formats['n_index'] = {
    'is_template': True,
    'format': {
        'align': 'center',
        'left': 1
    }
}

formats['fluxo'] = {
    'is_template': True,
    'format': {
        'bold': True,
        'num_format': '#,##0.00',
        'align': 'left'
    }
}

formats['date'] = {
    'is_template': True,
    'format': {
        'align': 'center',
        'right': 1
    }
}
