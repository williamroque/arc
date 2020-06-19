from curva.framework.tranche import *

from functools import reduce


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

        row = TrancheRow(formulae, pmt, amort, juros, saldo)
        self.queue = row

        return False

    self.next_phase()
    return True


def main_phase(self, _1, F_i, tranche_list, _2):
    row_sum = reduce(lambda acc, tranche: acc + tranche.queue.pmt, tranche_list[:-1], 0)

    juros = self.saldo * self.taxa_juros
    pmt = F_i * self.pmt_proper - row_sum
    amort = pmt - juros
    saldo = self.saldo + juros - pmt

    formulae = {
        'juros': '{prev_saldo}*{taxa_juros}',
        'pmt': '{F_i}*{pmt_proper}-{row_sum}',
        'amort': '{pmt}-{juros}',
        'saldo': '{prev_saldo}+{juros}-{pmt}'
    }

    row = TrancheRow(formulae, pmt, amort, juros, saldo)
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

    row = TrancheRow(formulae, pmt, amort, juros, saldo)
    self.queue = row

    self.next_phase()


class SeniorTranche(Tranche):
    def __init__(self, inputs):
        super().__init__(inputs, inputs.get('taxas-juros')['sen'], inputs.get('razoes')['sub'])

        self.title = 'Sênior'
        self.id = 'sen'

        self.phase_list = [
            carencia_phase, main_phase, final_phase
        ]
