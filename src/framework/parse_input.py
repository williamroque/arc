import sys
import json
import copy

import locale
import time


class Input():
    def __init__(self):
        self.raw_inputs = json.loads(sys.stdin.readlines()[0])

        self.indexador = self.raw_inputs['indexador']
        self.pu_emis = self.raw_inputs['pu-emis']
        self.total = self.raw_inputs['total']
        self.starting_date = self.raw_inputs['starting-date']
        self.razoes = self.raw_inputs['razoes']
        self.target_irr = self.raw_inputs['target-irr']
        self.taxas_juros = self.raw_inputs['taxas-juros']
        self.c_period = self.raw_inputs['c-period']
        self.fr_previsto = self.raw_inputs['fr-previsto']
        self.pmt_proper = self.raw_inputs['pmt-proper']
        self.despesas = self.raw_inputs['despesas']
        self.saldo_files = self.raw_inputs['planilhas-saldo']
        self.output_path = self.raw_inputs['output-path']
        self.appdata_path = self.raw_inputs['appdata-path']

        self.parse_inputs()

    def parse_inputs(self):
        for k, v in self.razoes.items():
            if type(v) == list:
                for i, razao in enumerate(v):
                    self.razoes[k][i] = razao / 100
            else:
                self.razoes[k] = v / 100

        self.taxas_juros_anual = self.taxas_juros
        for k, v in self.taxas_juros.items():
            if type(v) == list:
                for i, taxa in enumerate(v):
                    self.taxas_juros_anual[k][i] = taxa / 100
            else:
                self.taxas_juros_anual[k] = v / 100

        # To fix annoying reference 'feature'
        self.taxas_juros = copy.deepcopy(self.taxas_juros_anual)
        for k, v in self.taxas_juros_anual.items():
            if type(v) == list:
                for i, taxa in enumerate(v):
                    self.taxas_juros[k][i] = (taxa + 1) ** (1/12) - 1
            else:
                self.taxas_juros[k] = (v + 1) ** (1/12) - 1

        self.pmt_proper /= 100

        locale.setlocale(locale.LC_TIME, 'pt_BR')
        self.starting_date = time.strptime(self.starting_date, '%b/%Y')
