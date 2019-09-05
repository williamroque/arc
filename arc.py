import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import re

saldo_files = sys.argv[1:]

flux_evolution = {}

re_date = re.compile('^\s*[A-Z][a-z]{2}/\d{4}\s*$')

def parse_frame(df):
    h, w = df.shape

    evolution = []
    for col in range(w):
        if re_date.match(df.iloc[0, col]):
            evolution.append((
                df.iloc[0, col],
                df.iloc[h - 1, col]
            ))

    return evolution

evolution = {}
for file in saldo_files:
    df = pd.read_excel(file)
    parsed_df = parse_frame(df)
    for m in parsed_df:
        date, val = m
        if date in evolution:
            evolution[date].append(val)
        else:
            evolution[date] = [val]

total_evolution = [sum(evolution[m]) for m in evolution]
months = np.array([m for m in evolution])

fig, ax = plt.subplots(figsize=(20, 5))

ax.plot(np.arange(len(months)), total_evolution)
ax.grid()

x = np.arange(0, len(months), 3)
plt.xticks(x, months[x], rotation='vertical')

plt.tight_layout()
