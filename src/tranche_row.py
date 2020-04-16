class TrancheRow():
    def __init__(self, pmt, amort, juros, saldo, despesas=None):
        self.pmt = pmt
        self.amort = amort
        self.juros = juros
        self.saldo = saldo

    def render(self, worksheet, row, cell):
        raise NotImplementedError
