from curva.framework.tranche import Tranche

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

        for i in range(self.inputs.get('mezanine-layers-count')):
            tranche_mez = MezanineTranche(
                self.inputs,
                self.inputs.get('taxas-juros')['mezanino'][i],
                self.inputs.get('razoes')['mezanino'][i]
            )
            self.tranche_list.append(tranche_mez)

        tranche_sen = SeniorTranche(self.inputs)
        self.tranche_list.append(tranche_sen)

    def calculate_row(self, i, F_i, tranche_list):
        for tranche_i, tranche in enumerate(tranche_list):
            tranche.calculate(i, F_i, self.tranche_list, tranche_i)

    def run(self):
        fluxo_creditos = self.inputs.get('flux-total')
        for i in range(1, len(fluxo_creditos)):
            self.calculate_row(
                i,
                fluxo_creditos[i - 1],
                self.tranche_list
            )
            for tranche_i, tranche in enumerate(self.tranche_list):
                if tranche.queue and tranche.queue.saldo <= 0:
                    tranche.next_phase()
                    if tranche_i > 0:
                        self.tranche_list[tranche_i - 1].next_phase()

                    tranche.calculate(
                        i,
                        fluxo_creditos[i - 1],
                        self.tranche_list,
                        tranche_i
                    )

                    self.calculate_row(
                        i,
                        fluxo_creditos[i - 1],
                        self.tranche_list[:tranche_i]
                    )

                    break

            for tranche in self.tranche_list:
                if tranche.queue:
                    tranche.integrate_row()
                    tranche.saldo = tranche.queue.saldo

    def collapse_financial_flux(self):
        collapsed = [0 for _ in self.tranche_list[0].row_list]
        for tranche in self.tranche_list:
            for i, row in enumerate(tranche.row_list):
                collapsed[i] = collapsed[i] + row.juros + row.amort
        c_period = self.inputs.get('c-period')
        return [-self.inputs.get('total')] + [0 for _ in range(c_period)] + collapsed[c_period:]
