import tranche
import subordinate_tranche
import mezanine_tranche
import senior_tranche


class Session():
    def __init__(self, c_period, saldo, razoes_saldo, mezanine_count, taxas_juros, pmt_proper, despesas, fluxo_financeiro):
        self.c_period = c_period

        self.tranche_list = []
        self.final_tranche_list = []

        saldo_sub = saldo * razoes_saldo[0]
        taxa_juros_sub = taxas_juros[0]
        tranche_sub = subordinate_tranche.SubordinateTranche(
            'Subordinado', saldo_sub, taxa_juros_sub, pmt_proper, c_period, despesas
        )
        self.tranche_list.append(tranche_sub)

        for i in range(mezanine_count):
            saldo_mez = saldo * razoes_saldo[i + 1]
            taxa_juros_mez = taxas_juros[i + 1]
            tranche_mez = mezanine_tranche.MezanineTranche(
                'Mezanino', saldo_mez, taxa_juros_mez, pmt_proper, c_period
            )
            self.tranche_list.append(tranche_mez)

        saldo_sen = saldo * razoes_saldo[-1]
        taxa_juros_sen = taxas_juros[-1]
        tranche_sen = senior_tranche.SeniorTranche(
            'Sênior', saldo_sen, taxa_juros_sen, pmt_proper, c_period
        )
        self.tranche_list.append(tranche_sen)

        self.fluxo_financeiro = fluxo_financeiro

    def calculate_row(self, i, F_i, tranche_list):
        for tranche_i, tranche in enumerate(tranche_list):
            tranche.calculate(i, F_i, self.tranche_list, tranche_i)

    def run(self):
        for i, F_i in enumerate(self.fluxo_financeiro):
            self.calculate_row(i, self.fluxo_financeiro[i - 1], self.tranche_list)
            for tranche_i, tranche in enumerate(self.tranche_list):
                if tranche.queue and tranche.queue.saldo <= 0:
                    tranche.next_phase()
                    if tranche_i > 0:
                        self.tranche_list[tranche_i - 1].next_phase()

                    tranche.calculate(i, F_i, self.tranche_list, tranche_i)

                    self.calculate_row(i, self.fluxo_financeiro[i - 1], self.tranche_list[:tranche_i])

                    break

            for tranche in self.tranche_list:
                if tranche.queue:
                    tranche.integrate_row()
                    tranche.saldo = tranche.queue.saldo
                    print('{:,.2f}'.format(tranche.queue.saldo), tranche.queue.juros, tranche.queue.amort, tranche.queue.pmt, end=' | ')
            print()
