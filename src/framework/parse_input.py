import sys
import json

import locale
import time


class Input():
    def __init__(self):
        self.raw_inputs = json.loads(sys.stdin.readlines()[0])

        self.saldo_files = self.raw_inputs['inputFiles']
        self.output_path = self.raw_inputs['outputFile']
        self.indexador = self.raw_inputs['indexador']
        self.pu_emis = self.raw_inputs['pu-emis']
        self.total = self.raw_inputs['total']
        self.razoes = self.raw_inputs['razoes']
        self.target_irr = self.raw_inputs['target-irr']
        self.taxas_juros = self.raw_inputs['taxas-juros']
        self.c_period = self.raw_inputs['c-period']
        self.fr_previsto = self.raw_inputs['fr-previsto']
        self.pmt_proper = self.raw_inputs['pmt-proper']
        self.despesas = self.raw_inputs['despesas']
        self.starting_date = self.raw_inputs['starting-date']
        self.appdata_path = self.raw_inputs['appdata-path']

        self.parse_inputs()

    def parse_inputs(self):
        self.indexador = int(self.indexador)
        self.pu_emis = float(self.pu_emis)
        self.total = float(self.total)
        self.razoes = [float(razao) / 100 for razao in self.razoes]
        self.target_irr = float(self.target_irr)
        self.taxas_juros_anual = [float(taxa) / 100 for taxa in self.taxas_juros]
        self.taxas_juros = [
            (1 + float(taxa) / 100) ** (1/12) - 1 for taxa in self.taxas_juros
        ]
        self.c_period = int(self.c_period)
        self.fr_previsto = float(self.fr_previsto)
        self.pmt_proper = float(self.pmt_proper) / 100
        self.despesas = float(self.despesas)

        locale.setlocale(locale.LC_TIME, 'pt_BR')
        self.starting_date = time.strptime(self.starting_date, '%b/%Y')
