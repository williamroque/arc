from curva.framework.tranche import *


def presentation_phase(self, F_i, tranche_list, tranche_i):
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


def carencia_phase(self, F_i, tranche_list, tranche_i):
    if self.i < self.c_period + 1:
        juros = self.saldo * self.taxa_juros
        pmt = 0
        amort = 0
        saldo = self.saldo + self.despesas + juros - pmt

        row = self.create_row()
        row.fill('n', None, 'default')
        row.fill('data', None, 'default')
        row.fill('saldo', saldo, 'default')
        row.fill('despesas', None, 'default')
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
    pmt = juros + self.despesas
    amort = pmt - juros - self.despesas
    saldo = self.saldo + self.despesas + juros - pmt

    row = self.create_row()
    row.fill('n', None, 'default')
    row.fill('data', None, 'default')
    row.fill('saldo', saldo, 'default')
    row.fill('despesas', None, 'default')
    row.fill('juros', juros, 'default')
    row.fill('amort', amort, 'main')
    row.fill('pmt', pmt, 'dependent')
    row.fill('amort_perc', None, 'default')
    self.queue = row


def transition_phase(self, F_i, tranche_list, tranche_i):
    next_queue = tranche_list[1].queue

    juros = self.saldo * self.taxa_juros
    pmt = F_i * self.pmt_proper - next_queue.get_value('pmt')
    amort = pmt - juros - self.despesas
    saldo = self.saldo + self.despesas + juros - pmt

    row = self.create_row()
    row.fill('n', None, 'default')
    row.fill('data', None, 'default')
    row.fill('saldo', saldo, 'default')
    row.fill('despesas', None, 'default')
    row.fill('juros', juros, 'default')
    row.fill('amort', amort, 'main')
    row.fill('pmt', pmt, 'transition')
    row.fill('amort_perc', None, 'default')
    self.queue = row

    self.next_phase()


def main_phase(self, F_i, tranche_list, tranche_i):
    juros = self.saldo * self.taxa_juros
    pmt = F_i * self.pmt_proper
    amort = pmt - juros - self.despesas
    saldo = self.saldo + self.despesas + juros - pmt

    row = self.create_row()
    row.fill('n', None, 'default')
    row.fill('data', None, 'default')
    row.fill('saldo', saldo, 'default')
    row.fill('despesas', None, 'default')
    row.fill('juros', juros, 'default')
    row.fill('amort', amort, 'main')
    row.fill('pmt', pmt, 'main')
    row.fill('amort_perc', None, 'default')
    self.queue = row


def final_phase(self, F_i, tranche_list, tranche_i):
    juros = self.saldo * self.taxa_juros
    amort = self.saldo
    pmt = self.despesas + juros + amort
    saldo = self.saldo + self.despesas + juros - pmt

    row = self.create_row()
    row.fill('n', None, 'default')
    row.fill('data', None, 'default')
    row.fill('saldo', saldo, 'default')
    row.fill('despesas', None, 'default')
    row.fill('juros', juros, 'default')
    row.fill('amort', amort, 'final')
    row.fill('pmt', pmt, 'final')
    row.fill('amort_perc', None, 'default')
    self.queue = row

    self.next_phase()


class SubordinateTranche(Tranche):
    def __init__(self, inputs):
        super().__init__(inputs, inputs.get('taxas-juros')['sub'], inputs.get('razoes')['sub'], 'subordinado')

        self.title = 'Tranche Subordinado'

        self.phase_list = [
            presentation_phase, carencia_phase, dependent_phase, transition_phase, main_phase, final_phase
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
                'default': '={prev_saldo}+{despesas}+{juros}-{pmt}'
            },
            set(['tranche_quantity'])
        )
        row.add_column('despesas', 'Despesas', 10,
            {
                'empty': '',
                'default': f'={self.despesas}'
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
                'main': '={pmt}-{juros}-{despesas}',
                'final': '={prev_saldo}'
            },
            set(['tranche_quantity'])
        )
        row.add_column('pmt', 'PMT', 12,
            {
                'empty': '',
                'carencia': '=0',
                'dependent': '={juros}+{despesas}',
                'transition': '={F_i}*{pmt_proper}-{pmt_next}',
                'main': '={F_i}*{pmt_proper}',
                'final': '={despesas}+{juros}+{amort}'
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