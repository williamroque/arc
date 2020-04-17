class TrancheRow():
    def __init__(self, formulae, pmt, amort, juros, saldo, despesas=None):
        self.formulae = formulae
        self.pmt = pmt
        self.amort = amort
        self.juros = juros
        self.saldo = saldo
        self.despesas = despesas

    def render(self, worksheet, row, cell):
        pass
