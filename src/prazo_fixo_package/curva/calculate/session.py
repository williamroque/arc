from curva.calculate.subordinate_tranche import SubordinateTranche
from curva.calculate.senior_tranche import SeniorTranche


class Session():
    def __init__(self, inputs):
        self.inputs = inputs

        self.tranche_list = []
        self.final_tranche_list = []

        tranche_sub = SubordinateTranche(self.inputs)
        self.tranche_list.append(tranche_sub)

        tranche_sen = SeniorTranche(self.inputs)
        self.tranche_list.append(tranche_sen)

    def calculate_row(self, F_i, tranche_list):
        for tranche_i, tranche in enumerate(tranche_list):
            tranche.calculate(F_i, self.tranche_list, tranche_i)

    def run(self):
        fluxo_creditos = self.inputs.get('flux-total')
        for i in range(len(fluxo_creditos)):
            self.calculate_row(
                fluxo_creditos[i - 1],
                self.tranche_list
            )
            for tranche_i, tranche in enumerate(self.tranche_list):
                if tranche.queue and tranche.queue.get_value('saldo') <= 0:
                    tranche.next_phase()
                    if tranche_i > 0:
                        self.tranche_list[tranche_i - 1].next_phase()

                    tranche.calculate(
                        fluxo_creditos[i - 1],
                        self.tranche_list,
                        tranche_i
                    )

                    self.calculate_row(
                        fluxo_creditos[i - 1],
                        self.tranche_list[:tranche_i]
                    )

                    break

            for tranche in self.tranche_list:
                if tranche.queue:
                    tranche.integrate_row()
                    tranche.saldo = tranche.queue.get_value('saldo')

    def collapse_financial_flux(self):
        collapsed = [0 for _ in self.tranche_list[0].row_list]

        for tranche in self.tranche_list:
            for i, row in enumerate(tranche.row_list[1:]):
                collapsed[i] += row.get_value('juros') + row.get_value('amort')

        c_period = self.inputs.get('c-period')

        total_list = [-self.inputs.get('total')]
        carencia_list = [0 for _ in range(c_period)]

        return total_list + carencia_list + collapsed[c_period:]
