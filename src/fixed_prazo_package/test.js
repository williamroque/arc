const { spawn } = require('child_process');

const subprocess = spawn('python', ['main.py']);

const input = {
    indexador: 0,
    'pu-emis': 10000,
    total: 5180862.59,
    'starting-date': 'Set/2020',
    razoes: { sub: .58759485454718465, sen: .4124051454528155 },
    'target-prazos': [ 68, 11 ],
    'target-irr': .09,
    'taxas-juros-anual': { sen: .085, sub: -1 },
    'c-period': 0,
    'fr-previsto': 0,
    'pmt-proper': .92,
    despesas: 15000,
    'planilhas-saldo': [
        '/Users/jetblack-work/downloads/Saldo 7ª8ª - 31.08.2020.xlsx'
    ],
    'primeira-serie': 7,
    'output-path': '/Users/jetblack-work/Desktop/new_7_8.xlsx',
    'appdata-path': '/Users/jetblack-work/Library/Application Support/Arc'
};

subprocess.stdin.write(JSON.stringify(input));
subprocess.stdin.end();

subprocess.stderr.on('data', err => {
    console.log(err.toString());
});

subprocess.stdout.on('data', out => {
    console.log(out.toString());
});
