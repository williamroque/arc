import pandas as pd
import numpy as np

import time
import locale

import re

# EXPECTED FORMAT for SALDO FILE:
#  _______________________________
# |__...__|___*MONTH___|__Total__|
# |__...__|_____...____|___...___|
# |__...__|___*VALUE___|___...___|

locale.setlocale(locale.LC_TIME, 'pt_BR')


class Flux():
    def __init__(self, saldo_files, starting_date):
        self.starting_date = starting_date

        self.flux_total = {}

        for file in saldo_files:
            df = pd.read_excel(file)
            self.parse_frame(df)

        self.collapsed_flux = []
        self.months = []

    def collapse(self):
        for month, values in self.flux_total.items():
            self.collapsed_flux.append(sum(values))
            self.months.append(month)

        return self.collapsed_flux

    def parse_frame(self, df):
        re_date = re.compile('^\s*[A-Z][a-z]{2}/\d{4}\s*$')

        height, width = df.shape

        for col_i in range(width):
            if re_date.match(df.iloc[0, col_i]):
                raw_date = df.iloc[0, col_i]
                parsed_date = time.strptime(raw_date, '%b/%Y')

                parsed_year = parsed_date.tm_year
                parsed_month = parsed_date.tm_mon
                starting_year = self.starting_date.tm_year
                starting_month = self.starting_date.tm_mon

                if parsed_year > starting_year or parsed_year == starting_year and parsed_month >= starting_month:
                    value = df.iloc[height - 1, col_i]
                    if value > 0:
                        formatted_date = time.strftime('%b-%y', parsed_date)

                        if not formatted_date in self.flux_total:
                            self.flux_total[formatted_date] = []

                        self.flux_total[formatted_date].append(value)
