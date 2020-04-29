import tranche
import tranche_row


def carencia_phase(self, i, *_):
    if self.i < self.c_period:
        juros = self.saldo * self.taxa_juros
        pmt = 0
        amort = 0
        saldo = self.saldo + self.despesas + juros - pmt

        formulae = {
            'juros': '{prev_saldo}*{taxa_juros}',
            'pmt': '0',
            'amort': '0',
            'saldo': '{prev_saldo}+{despesas}+{juros}-{pmt}'
        }

        row = tranche_row.TrancheRow(
            formulae, pmt, amort, juros, saldo, self.despesas)
        self.queue = row

        return False

    self.next_phase()
    return True


def dependent_phase(self, *_):
    juros = self.saldo * self.taxa_juros
    pmt = juros + self.despesas
    amort = pmt - juros - self.despesas
    saldo = self.saldo + self.despesas + juros - pmt

    formulae = {
        'juros': '{prev_saldo}*{taxa_juros}',
        'pmt': '{juros}+{despesas}',
        'amort': '{pmt}-{juros}-{despesas}',
        'saldo': '{prev_saldo}+{despesas}+{juros}-{pmt}'
    }

    row = tranche_row.TrancheRow(
        formulae, pmt, amort, juros, saldo, self.despesas)
    self.queue = row


def transition_phase(self, _1, F_i, tranche_list, _2):
    juros = self.saldo * self.taxa_juros
    pmt = F_i * self.pmt_proper - tranche_list[1].queue.pmt
    amort = pmt - juros - self.despesas
    saldo = self.saldo + self.despesas + juros - pmt

    formulae = {
        'juros': '{prev_saldo}*{taxa_juros}',
        'pmt': '{F_i}*{pmt_proper}-{pmt_next}',
        'amort': '{pmt}-{juros}-{despesas}',
        'saldo': '{prev_saldo}+{despesas}+{juros}-{pmt}'
    }

    row = tranche_row.TrancheRow(
        formulae, pmt, amort, juros, saldo, self.despesas)
    self.queue = row

    self.next_phase()


def main_phase(self, i, F_i, *_2):
    juros = self.saldo * self.taxa_juros
    pmt = F_i * self.pmt_proper
    amort = pmt - juros - self.despesas
    saldo = self.saldo + self.despesas + juros - pmt

    formulae = {
        'juros': '{prev_saldo}*{taxa_juros}',
        'pmt': '{F_i}*{pmt_proper}',
        'amort': '{pmt}-{juros}-{despesas}',
        'saldo': '{prev_saldo}+{despesas}+{juros}-{pmt}'
    }

    row = tranche_row.TrancheRow(
        formulae, pmt, amort, juros, saldo, self.despesas)
    self.queue = row


def final_phase(self, *_):
    juros = self.saldo * self.taxa_juros
    amort = self.saldo
    pmt = self.despesas + juros + amort
    saldo = self.saldo + self.despesas + juros - pmt

    formulae = {
        'juros': '{prev_saldo}*{taxa_juros}',
        'pmt': '{despesas}+{juros}+{amort}',
        'amort': '{prev_saldo}',
        'saldo': '{prev_saldo}+{despesas}+{juros}-{pmt}'
    }

    row = tranche_row.TrancheRow(
        formulae, pmt, amort, juros, saldo, self.despesas)
    self.queue = row

    self.next_phase()


class SubordinateTranche(tranche.Tranche):
    def __init__(self, title, saldo, taxa_juros, pmt_proper, c_period, despesas):
        super().__init__(title, saldo, taxa_juros, pmt_proper, c_period, despesas)

        self.phase_list = [
            carencia_phase, dependent_phase, transition_phase, main_phase, final_phase
        ]

    def render(self, worksheet, row, cell, headers):
        pass
