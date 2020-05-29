import tranche
import subordinate_tranche
import mezanine_tranche
import senior_tranche


class Session():
    def __init__(self, c_period, saldo, razoes, taxas_juros, pmt_proper, despesas, fluxo_creditos):
        self.c_period = c_period

        self.tranche_list = []
        self.final_tranche_list = []

        self.total = saldo

        saldo_sub = saldo * razoes['sub']
        taxa_juros_sub = taxas_juros['sub']
        tranche_sub = subordinate_tranche.SubordinateTranche(
            saldo_sub, taxa_juros_sub, pmt_proper, c_period, despesas
        )
        self.tranche_list.append(tranche_sub)

        for i in range(len(razoes['mezanino'])):
            saldo_mez = saldo * razoes['mezanino'][i]
            taxa_juros_mez = taxas_juros['mezanino'][i]
            tranche_mez = mezanine_tranche.MezanineTranche(
                saldo_mez, taxa_juros_mez, pmt_proper, c_period
            )
            self.tranche_list.append(tranche_mez)

        saldo_sen = saldo * razoes['sen']
        taxa_juros_sen = taxas_juros['sen']
        tranche_sen = senior_tranche.SeniorTranche(
            saldo_sen, taxa_juros_sen, pmt_proper, c_period
        )
        self.tranche_list.append(tranche_sen)

        self.fluxo_creditos = fluxo_creditos

    def calculate_row(self, i, F_i, tranche_list):
        for tranche_i, tranche in enumerate(tranche_list):
            tranche.calculate(i, F_i, self.tranche_list, tranche_i)

    def run(self):
        for i in range(1, len(self.fluxo_creditos)):
            self.calculate_row(
                i,
                self.fluxo_creditos[i - 1],
                self.tranche_list
            )
            for tranche_i, tranche in enumerate(self.tranche_list):
                if tranche.queue and tranche.queue.saldo <= 0:
                    tranche.next_phase()
                    if tranche_i > 0:
                        self.tranche_list[tranche_i - 1].next_phase()

                    tranche.calculate(i, self.fluxo_creditos[i - 1], self.tranche_list, tranche_i)

                    self.calculate_row(
                        i,
                        self.fluxo_creditos[i - 1],
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
        return [-self.total] + [0 for _ in range(self.c_period)] + collapsed[self.c_period:]
