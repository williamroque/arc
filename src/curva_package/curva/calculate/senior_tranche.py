from curva.framework.tranche import *

from functools import reduce


def presentation_phase(self, F_i, tranche_list, tranche_i):
    row = self.create_row()
    row.fill('n', None, 'default')
    row.fill('data', None, 'default')
    row.fill('saldo', self.saldo, 'presentation')
    row.fill('juros', None, 'empty')
    row.fill('amort', None, 'empty')
    row.fill('pmt', None, 'empty')
    row.fill('amort_perc', None, 'empty')
    self.queue = row

    self.next_phase()


def carencia_phase(self, F_i, tranche_list, tranche_i):
    if self.i < self.c_period + 1:
        juros = self.saldo * self.taxa_juros
        pmt = 0
        amort = 0
        saldo = self.saldo + juros - pmt

        row = self.create_row()
        row.fill('n', None, 'default')
        row.fill('data', None, 'default')
        row.fill('saldo', saldo, 'default')
        row.fill('juros', juros, 'default')
        row.fill('amort', amort, 'carencia')
        row.fill('pmt', pmt, 'carencia')
        row.fill('amort_perc', None, 'default')
        self.queue = row

        return False

    self.next_phase()
    return True


def main_phase(self, F_i, tranche_list, tranche_i):
    other_tranches = tranche_list[:-1]

    row_sum = 0
    for tranche in other_tranches:
        row_sum += tranche.queue.get_value('pmt')

    juros = self.saldo * self.taxa_juros
    pmt = F_i * self.pmt_proper - row_sum
    amort = pmt - juros
    saldo = self.saldo + juros - pmt

    row = self.create_row()
    row.fill('n', None, 'default')
    row.fill('data', None, 'default')
    row.fill('saldo', saldo, 'default')
    row.fill('juros', juros, 'default')
    row.fill('amort', amort, 'main')
    row.fill('pmt', pmt, 'main')
    row.fill('amort_perc', None, 'default')
    self.queue = row


def final_phase(self, F_i, tranche_list, tranche_i):
    juros = self.saldo * self.taxa_juros
    amort = self.saldo
    pmt = juros + amort
    saldo = self.saldo + juros - pmt

    row = self.create_row()
    row.fill('n', None, 'default')
    row.fill('data', None, 'default')
    row.fill('saldo', saldo, 'default')
    row.fill('juros', juros, 'default')
    row.fill('amort', amort, 'final')
    row.fill('pmt', pmt, 'final')
    row.fill('amort_perc', None, 'default')
    self.queue = row

    self.next_phase()


class SeniorTranche(Tranche):
    def __init__(self, inputs):
        super().__init__(inputs, inputs.get('taxas-juros')['sen'], inputs.get('razoes')['sen'], 'senior')

        self.title = 'Tranche Sênior'

        self.phase_list = [
            presentation_phase, carencia_phase, main_phase, final_phase
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
                'presentation': '={original_saldo}',
                'default': '={prev_saldo}+{juros}-{pmt}'
            },
            set(['tranche_quantity'])
        )
        row.add_column('juros', 'Juros', 12,
            {
                'empty': '',
                'default': '={prev_saldo}*{taxa_juros}'
            },
            set(['tranche_quantity'])
        )
        row.add_column('amort', 'Amortiz', 12,
            {
                'empty': '',
                'carencia': '=0',
                'main': '={pmt}-{juros}',
                'final': '={prev_saldo}'
            },
            set(['tranche_quantity'])
        )
        row.add_column('pmt', 'PMT', 12,
            {
                'empty': '',
                'carencia': '=0',
                'main': '={F_i}*{pmt_proper}-{row_sum}',
                'final': '={juros}+{amort}'
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
