import pandas as pd

import time
import locale

# EXPECTED FORMAT for SALDO FILE:
#  _______________________________
# |__...__|_____...____|___...___|
# |__...__|___*MONTH___|___...___|
# |__...__|_____...____|___...___|
# |__...__|___*VALUE___|___...___|

locale.setlocale(locale.LC_TIME, 'pt_BR')


class Flux():
    def __init__(self, saldo_files, starting_date):
        self.flux_total = {}

        for file in saldo_files:
            df = pd.read_excel(file)
            df.columns = df.iloc[0]

            parsed_df = df.loc[:, df.iloc[0].str.contains(
                r'[A-Za-z]{3}/\d{4}'
            )].iloc[-1]

            for date, value in dict(parsed_df).items():
                if time.strptime(date, '%b/%Y') >= starting_date:
                    if date in self.flux_total:
                        self.flux_total[date] += value
                    else:
                        self.flux_total[date] = value

    def get_flux(self):
        return (
            list(self.flux_total.keys()),
            list(self.flux_total.values())
        )
