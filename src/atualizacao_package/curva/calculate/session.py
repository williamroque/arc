from itertools import zip_longest

from curva.calculate.subordinate_tranche import SubordinateTranche
from curva.calculate.mezanine_tranche import MezanineTranche
from curva.calculate.senior_tranche import SeniorTranche


class Session():
    def __init__(self, inputs):
        self.inputs = inputs

        self.tranche_list = []
        self.final_tranche_list = []

        tranche_sub = SubordinateTranche(self.inputs)
        self.tranche_list.append(tranche_sub)

        for i in range(self.inputs.get('curve')['mezanine-layers-count']):
            tranche_mez = MezanineTranche(
                self.inputs,
                self.inputs.get('curve')['taxas-juros']['mezanino'][i],
                self.inputs.get('curve')['razoes']['mezanino'][i],
                f'mezanino-{i}'
            )
            self.tranche_list.append(tranche_mez)

        tranche_sen = SeniorTranche(self.inputs)
        self.tranche_list.append(tranche_sen)

    def calculate_row(self, tranche_list):
        for tranche_i, tranche in enumerate(tranche_list):
            tranche.calculate(self.tranche_list, tranche_i)

    def run(self):
        fluxo_creditos = self.inputs.get('flux-total')
        for i in range(len(fluxo_creditos)):
            self.calculate_row(
                self.tranche_list
            )

            for tranche in self.tranche_list:
                if tranche.queue:
                    tranche.integrate_row()
                    tranche.saldo = tranche.queue.get_value('saldo')

    def collapse_financial_flux(self):
        collapsed = [0 for _ in self.tranche_list[0].row_list]

        for tranche in self.tranche_list:
            for i, row in enumerate(tranche.row_list[1:]):
                collapsed[i] += row.get_value('pmt')

        total = [-self.inputs.get('curve')['total']]

        return total + collapsed
