from curva.framework.tranche import *


def carencia_phase(self, F_i, tranche_list, tranche_i):
    if self.i < self.c_period:
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


def dependent_phase(self, F_i, tranche_list, tranche_i):
    juros = self.saldo * self.taxa_juros
    pmt = juros
    amort = pmt - juros
    saldo = self.saldo + juros - pmt

    row = self.create_row()
    row.fill('n', None, 'default')
    row.fill('data', None, 'default')
    row.fill('saldo', saldo, 'default')
    row.fill('juros', juros, 'default')
    row.fill('amort', amort, 'main')
    row.fill('pmt', pmt, 'dependent')
    row.fill('amort_perc', None, 'default')
    self.queue = row


def transition_phase(self, F_i, tranche_list, tranche_i):
    next_queue = tranche_list[tranche_i + 1].queue

    juros = self.saldo * self.taxa_juros
    pmt = F_i * self.pmt_proper - next_queue.get_value('pmt')
    amort = pmt - juros
    saldo = self.saldo + juros - pmt

    row = self.create_row()
    row.fill('n', None, 'default')
    row.fill('data', None, 'default')
    row.fill('saldo', saldo, 'default')
    row.fill('juros', juros, 'default')
    row.fill('amort', amort, 'main')
    row.fill('pmt', pmt, 'transition')
    row.fill('amort_perc', None, 'default')
    self.queue = row

    self.next_phase()


def main_phase(self, F_i, tranche_list, tranche_i):
    juros = self.saldo * self.taxa_juros
    pmt = F_i * self.pmt_proper
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


class MezanineTranche(Tranche):
    def __init__(self, inputs, taxa_juros, razao):
        super().__init__(inputs, taxa_juros, razao)

        self.title = 'Tranche Mezanino'

        self.phase_list = [
            carencia_phase, dependent_phase, transition_phase, main_phase, final_phase
        ]

    def create_row(self):
        row = TrancheRow()
        row.add_column('n', 'N', 6,
            {'default': '{i}'}
        )
        row.add_column('data', 'Data', 8,
            {'default': '{data}'}
        )
        row.add_column('saldo', 'Saldo Devedor', 13,
            {'default': '{prev_saldo}*{taxa_juros}'}
        )
        row.add_column('juros', 'Juros', 12,
            {'default': '{prev_saldo}*{taxa_juros}'}
        )
        row.add_column('amort', 'Amortiz', 12,
            {
                'carencia': '0',
                'main': '{pmt}-{juros}',
                'final': '{prev_saldo}'
            }
        )
        row.add_column('pmt', 'PMT', 12,
            {
                'carencia': '0',
                'dependent': '{juros}',
                'transition': '{F_i}*{pmt_proper}-{pmt_next}',
                'main': '{F_i}*{pmt_proper}',
                'final': '{juros}+{amort}'
            }
        )
        row.add_column('amort_perc', '% AM', 10,
            {'default': '{amort}/{prev_saldo}'}
        )

        return row