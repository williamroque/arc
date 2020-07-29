from curva.framework.tranche import *


def presentation_phase(self, tranche_list, tranche_i):
    row = self.create_row()
    row.fill('n', None, 'default')
    row.fill('data', None, 'default')
    row.fill('saldo', self.saldo, 'presentation')
    row.fill('despesas', None, 'empty')
    row.fill('juros', None, 'empty')
    row.fill('amort', None, 'empty')
    row.fill('pmt', None, 'empty')
    row.fill('amort_perc', None, 'empty')
    self.queue = row

    self.next_phase()


def draw_phase(self, tranche_list, tranche_i):
    historical_period = self.inputs.get('historical-period')
    adjusted_i = self.i - self.phase_first_index
    layers_count = self.inputs.get('curve')['mezanine-layers-count'] + 2

    if adjusted_i < historical_period:
        serie = str(layers_count - 1 - tranche_i + self.inputs.get('curve')['primeira-serie'])
        historical_row = self.inputs.get('curve')['atual'][serie][self.i - self.phase_first_index]

        juros = historical_row[0]
        saldo = historical_row[3]

        row = self.create_row()
        row.fill('n', None, 'default')
        row.fill('data', None, 'default')
        row.fill('despesas', None, 'default')
        row.fill('saldo', saldo, 'historical', {'saldo-historical': saldo})
        row.fill('juros', juros, 'historical', {'juros-historical': juros})

        if self.i - 1 < self.inputs.get('curve')['c-period']:
            amort = 0
            pmt = 0

            row.fill('amort', amort, 'carencia')
            row.fill('pmt', pmt, 'carencia')
        else:
            amort = historical_row[1] + historical_row[2]
            pmt = juros + amort

            row.fill('amort', amort, 'historical', {'amort-historical': amort})
            row.fill('pmt', pmt, 'main')

        row.fill('amort_perc', amort/saldo, 'default')
        self.queue = row

        return False

    self.next_phase()
    return True


def carencia_phase(self, tranche_list, tranche_i):
    if self.i - 1 < self.inputs.get('curve')['c-period']:
        juros = self.saldo * self.taxa_juros
        pmt = 0
        amort = 0
        saldo = self.saldo + juros - amort

        row = self.create_row()
        row.fill('n', None, 'default')
        row.fill('data', None, 'default')
        row.fill('saldo', saldo, 'carencia')
        row.fill('despesas', None, 'default')
        row.fill('juros', juros, 'default')
        row.fill('amort', amort, 'carencia')
        row.fill('pmt', pmt, 'carencia')
        row.fill('amort_perc', amort/self.saldo, 'default')
        self.queue = row

        return False

    self.next_phase()
    return True


def main_phase(self, tranche_list, tranche_i):
    juros = self.saldo * self.taxa_juros
    amort = self.inputs.get('curve')['amort-percentages']['subordinado'][self.i] * self.saldo
    pmt = juros + amort
    saldo = self.saldo - amort

    row = self.create_row()
    row.fill('n', None, 'default')
    row.fill('data', None, 'default')
    row.fill('saldo', saldo, 'default')
    row.fill('despesas', None, 'default')
    row.fill('juros', juros, 'default')
    row.fill('amort', amort, 'main')
    row.fill('pmt', pmt, 'main')
    row.fill('amort_perc', amort/self.saldo, 'default')
    self.queue = row

    if saldo <= 0:
        self.next_phase()


class SubordinateTranche(Tranche):
    def __init__(self, inputs):
        super().__init__(inputs, inputs.get('curve')['taxas-juros']['sub'], inputs.get('curve')['razoes']['sub'], 'subordinado')

        self.title = 'Tranche Subordinado'

        self.phase_list = [
            presentation_phase, draw_phase, carencia_phase, main_phase
        ]

    def create_row(self):
        row = TrancheRow()
        row.add_column('n', 'N', 6,
            {'default': '={i}'},
            set(['index'])
        )
        row.add_column('data', 'Data', 8,
            {'default': '{data}'},
            set(['date'])
        )
        row.add_column('saldo', 'Saldo Devedor', 13,
            {
                'presentation': '={valor_total}*{razao}',
                'historical': '={saldo_historical}',
                'carencia': '={prev_saldo}+{juros}-{amort}',
                'default': '={prev_saldo}-{amort}'
            },
            set(['tranche_quantity'])
        )
        row.add_column('despesas', 'Despesas', 10,
            {
                'empty': '',
                'historical': '={juros_historical}',
                'default': '={}'.format(self.inputs.get('curve')['despesas'])
            },
            set(['tranche_quantity'])
        )
        row.add_column('juros', 'Juros', 12,
            {
                'empty': '',
                'historical': '={juros_historical}',
                'default': '={prev_saldo}*{taxa_juros}'
            },
            set(['tranche_quantity'])
        )
        row.add_column('amort', 'Amortiz', 12,
            {
                'empty': '',
                'historical': '={amort_historical}',
                'carencia': '=0',
                'main': '={amort_perc}*{prev_saldo}'
            },
            set(['tranche_quantity'])
        )
        row.add_column('pmt', 'PMT', 12,
            {
                'empty': '',
                'historical': '={juros}+{amort}',
                'carencia': '=0',
                'main': '={juros}+{amort}'
            },
            set(['tranche_quantity'])
        )
        row.add_column('amort_perc', '% AM', 10,
            {
                'empty': '',
                'default': '={amort}/{prev_saldo}'
            },
            set(['tranche_percentage'])
        )

        return row