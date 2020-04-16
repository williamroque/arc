import sys
import json

import locale
import time


class Input():
    def __init__(self):
        self.raw_inputs = json.loads(sys.stdin.readlines()[0])

        self.saldo_files       = self.raw_inputs['inputFiles']
        self.output_path       = self.raw_inputs['outputFile']
        self.indexador         = self.raw_inputs['indexador']
        self.pu_emis           = self.raw_inputs['pu-emis']
        self.total             = self.raw_inputs['total']
        self.r_sen             = self.raw_inputs['r-sen']
        self.r_sub             = self.raw_inputs['r-sub']
        self.target_irr        = self.raw_inputs['target-irr']
        self.t_em_senior_anual = self.raw_inputs['t-em-senior-anual']
        self.c_period          = self.raw_inputs['c-period']
        self.fr_previsto       = self.raw_inputs['fr-previsto']
        self.pmt_proper        = self.raw_inputs['pmt-proper']
        self.despesas          = self.raw_inputs['despesas']
        self.starting_date     = self.raw_inputs['starting-date']
        self.mezanine_layers   = self.raw_inputs['mezanine-layers']


        self.parse_inputs()

    def parse_inputs(self):
        self.indexador = int(self.indexador)
        self.pu_emis = float(self.pu_emis)
        self.total = float(self.pu_emis)
        self.r_sen = float(self.r_sen) / 100
        self.r_sub = float(self.r_sub) / 100
        self.target_irr = float(self.target_irr)

        self.t_em_senior_anual = float(self.t_em_senior_anual) / 100
        self.t_em_senior = (1 + self.t_em_senior_anual) ** (1/12) - 1

        self.c_period = int(self.c_period)
        self.fr_previsto = float(self.fr_previsto)
        self.pmt_proper = float(self.pmt_proper) / 100
        self.despesas = float(self.despesas)

        locale.setlocale(locale.LC_TIME, 'pt_BR')
        self.starting_date = time.strptime(self.starting_date, '%b/%Y')

        for layer in self.mezanine_layers:
            layer[1] = float(layer[1]) / 100
            layer[2] = float(layer[2]) / 100

