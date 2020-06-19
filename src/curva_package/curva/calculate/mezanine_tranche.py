from curva.framework.tranche import *


def carencia_phase(self, i, F_i, tranche_list, tranche_i):
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

        row = TrancheRow(formulae, pmt, amort, juros, saldo)
        self.queue = row

        return False

    self.next_phase()
    return True


def dependent_phase(self, i, F_i, tranche_list, tranche_i):
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

    row = TrancheRow(formulae, pmt, amort, juros, saldo)
    self.queue = row


def transition_phase(self, i, F_i, tranche_list, tranche_i):
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

    row = TrancheRow(formulae, pmt, amort, juros, saldo)
    self.queue = row

    self.next_phase()


def main_phase(self, i, F_i, tranche_list, tranche_i):
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

    row = TrancheRow(formulae, pmt, amort, juros, saldo)
    self.queue = row


def final_phase(self, i, F_i, tranche_list, tranche_i):
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

    row = TrancheRow(formulae, pmt, amort, juros, saldo)
    self.queue = row

    self.next_phase()


class MezanineTranche(Tranche):
    def __init__(self, inputs, taxa_juros, razao):
        super().__init__(inputs, taxa_juros, razao)

        self.title = 'Mezanino'
        self.id = 'mezanino'

        self.phase_list = [
            carencia_phase, dependent_phase, transition_phase, main_phase, final_phase
        ]
