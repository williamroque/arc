import tranche
import tranche_row


def carencia_phase(self, i, *_):
    if self.i < self.c_period:
        juros = self.saldo * self.taxa_juros
        pmt = 0
        amort = 0
        saldo = self.saldo + juros - pmt

        formulae = {
            'juros': '{prev_saldo}*{taxa_juros}',
            'pmt': '0',
            'amort': '0',
            'saldo': '{prev_saldo}+{juros}-{pmt}'
        }

        row = tranche_row.TrancheRow(formulae, pmt, amort, juros, saldo)
        self.queue = row

        return False

    self.next_phase()
    return True


def dependent_phase(self, *_):
    juros = self.saldo * self.taxa_juros
    pmt = juros
    amort = pmt - juros
    saldo = self.saldo + juros - pmt

    formulae = {
        'juros': '{prev_saldo}*{taxa_juros}',
        'pmt': '{juros}',
        'amort': '{pmt}-{juros}',
        'saldo': '{prev_saldo}+{juros}-{pmt}'
    }

    row = tranche_row.TrancheRow(formulae, pmt, amort, juros, saldo)
    self.queue = row


def transition_phase(self, _, F_i, tranche_list, tranche_i):
    juros = self.saldo * self.taxa_juros
    pmt = F_i * self.pmt_proper - tranche_list[tranche_i + 1].queue.pmt
    amort = pmt - juros
    saldo = self.saldo + juros - pmt

    formulae = {
        'juros': '{prev_saldo}*{taxa_juros}',
        'pmt': '{F_i}*{pmt_proper}-{pmt_next}',
        'amort': '{pmt}-{juros}',
        'saldo': '{prev_saldo}+{juros}-{pmt}'
    }

    row = tranche_row.TrancheRow(formulae, pmt, amort, juros, saldo)
    self.queue = row

    self.next_phase()


def main_phase(self, _1, F_i, *_2):
    juros = self.saldo * self.taxa_juros
    pmt = F_i * self.pmt_proper
    amort = pmt - juros
    saldo = self.saldo + juros - pmt

    formulae = {
        'juros': '{prev_saldo}*{taxa_juros}',
        'pmt': '{F_i}*{pmt_proper}',
        'amort': '{pmt}-{juros}',
        'saldo': '{prev_saldo}+{juros}-{pmt}'
    }

    row = tranche_row.TrancheRow(formulae, pmt, amort, juros, saldo)
    self.queue = row


def final_phase(self, *_):
    juros = self.saldo * self.taxa_juros
    amort = self.saldo
    pmt = juros + amort
    saldo = self.saldo + juros - pmt

    formulae = {
        'juros': '{prev_saldo}*{taxa_juros}',
        'pmt': '{juros}+{amort}',
        'amort': '{prev_saldo}',
        'saldo': '{prev_saldo}+{juros}-{pmt}'
    }

    row = tranche_row.TrancheRow(formulae, pmt, amort, juros, saldo)
    self.queue = row

    self.next_phase()


class MezanineTranche(tranche.Tranche):
    def __init__(self, title, saldo, taxa_juros, pmt_proper, c_period):
        super().__init__(title, saldo, taxa_juros, pmt_proper, c_period)

        self.phase_list = [
            carencia_phase, dependent_phase, transition_phase, main_phase, final_phase
        ]

    def render(self, worksheet, row, cell, headers):
        pass
