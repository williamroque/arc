from curva.framework.tranche import *


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


def draw_phase(self, F_i, tranche_list, tranche_i):
    if self.i - self.phase_first_index < self.inputs.get('historical-period'):
        serie = str(self.inputs.get('curve')['mezanine-layers-count'] + 2 - tranche_i + self.inputs.get('curve')['primeira-serie'])
        historical_row = self.inputs.get('curve')['atual'][serie][self.i - self.phase_first_index]

        juros = historical_row[0]
        amort = historical_row[1] + historical_row[2]
        pmt = juros + amort
        saldo = historical_row[3]

        row = self.create_row()
        row.fill('n', None, 'default')
        row.fill('data', None, 'default')
        row.fill('saldo', saldo, 'historical', {'saldo-historical': saldo})
        row.fill('juros', juros, 'historical', {'juros-historical': juros})
        row.fill('amort', amort, 'historical', {'amort-historical': amort})
        row.fill('pmt', pmt, 'historical')
        row.fill('amort_perc', amort/saldo, 'default')
        self.queue = row

        return False
    
    self.next_phase()
    return True


def carencia_phase(self, F_i, tranche_list, tranche_i):
    if self.i - self.phase_first_index < self.inputs.get('curve')['c-period']:
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
        row.fill('amort_perc', amort/self.saldo, 'default')
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
    row.fill('amort_perc', amort/self.saldo, 'default')
    self.queue = row


def transition_phase(self, F_i, tranche_list, tranche_i):
    next_queue = tranche_list[tranche_i + 1].queue

    juros = self.saldo * self.taxa_juros
    pmt = F_i * self.inputs.get('curve')['pmt-proper'] - next_queue.get_value('pmt')
    amort = pmt - juros
    saldo = self.saldo + juros - pmt

    row = self.create_row()
    row.fill('n', None, 'default')
    row.fill('data', None, 'default')
    row.fill('saldo', saldo, 'default')
    row.fill('juros', juros, 'default')
    row.fill('amort', amort, 'main')
    row.fill('pmt', pmt, 'transition')
    row.fill('amort_perc', amort/self.saldo, 'default')
    self.queue = row

    self.next_phase()


def main_phase(self, F_i, tranche_list, tranche_i):
    juros = self.saldo * self.taxa_juros
    pmt = F_i * self.inputs.get('curve')['pmt-proper']
    amort = pmt - juros
    saldo = self.saldo + juros - pmt

    row = self.create_row()
    row.fill('n', None, 'default')
    row.fill('data', None, 'default')
    row.fill('saldo', saldo, 'default')
    row.fill('juros', juros, 'default')
    row.fill('amort', amort, 'main')
    row.fill('pmt', pmt, 'main')
    row.fill('amort_perc', amort/self.saldo, 'default')
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
    row.fill('amort_perc', amort/self.saldo, 'default')
    self.queue = row

    self.next_phase()


class MezanineTranche(Tranche):
    def __init__(self, inputs, taxa_juros, razao, tranche_id):
        super().__init__(inputs, taxa_juros, razao, tranche_id)

        self.title = 'Tranche Mezanino'

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
                'historical': '={saldo_historical}',
                'default': '={prev_saldo}+{juros}-{pmt}'
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
                'main': '={pmt}-{juros}',
                'final': '={prev_saldo}'
            },
            set(['tranche_quantity'])
        )
        row.add_column('pmt', 'PMT', 12,
            {
                'empty': '',
                'historical': '={juros}+{amort}',
                'carencia': '=0',
                'dependent': '={juros}',
                'transition': '={F_i}*{pmt_proper}-{pmt_next}',
                'main': '={F_i}*{pmt_proper}',
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