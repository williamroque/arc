class Tranche():
    def __init__(self, saldo, taxa_juros, pmt_proper, c_period, despesas=None):
        self.saldo_original = saldo

        self.saldo = saldo
        self.taxa_juros = taxa_juros
        self.pmt_proper = pmt_proper
        self.c_period = c_period
        self.despesas = despesas

        self.is_finished = False
        self.phase_list = []
        self.row_list = []

        self.queue = None

        self.i = 0

    def next_phase(self):
        self.phase_list = self.phase_list[1:]

    def integrate_row(self):
        if self.queue:
            self.row_list.append(self.queue)
            self.i += 1

    def get_previous_row(self):
        return self.row_list[-1]

    def get_completion_state(self):
        if self.saldo <= 0:
            self.is_finished = True
            return True
        return False

    def calculate(self, i, F_i, tranche_list, tranche_i):
        if len(self.phase_list):
            repeats_calculation = self.phase_list[0](self, i, F_i, tranche_list, tranche_i)
            if repeats_calculation:
                self.phase_list[0](self, i, F_i, tranche_list, tranche_i)
        else:
            self.queue = None


class TrancheRow():
    def __init__(self, formulae, pmt, amort, juros, saldo, despesas=None):
        self.formulae = formulae
        self.pmt = pmt
        self.amort = amort
        self.juros = juros
        self.saldo = saldo
        self.despesas = despesas
