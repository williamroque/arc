const { spawn } = require('child_process');

const subprocess = spawn('python3', ['main.py']);

const input = {
    indexador: 0,
    'pu-emis': 1000,
    total: 14270000,
    'starting-date': 'Set/2019',
    razoes: { sub: .15, sen: .70, mezanino: [.15] },
    'target-irr': 10.5,
    'taxas-juros-anual': { sen: .07, mezanino: [.085] },
    'c-period': 3,
    'fr-previsto': 400000,
    'pmt-proper': .92,
    despesas: 10000,
    'planilhas-saldo': [
        '/Users/jetblack-work/Documents/Curve/arc/samples/1/saldos/1.xlsx',
        '/Users/jetblack-work/Documents/Curve/arc/samples/1/saldos/2.xlsx',
        '/Users/jetblack-work/Documents/Curve/arc/samples/1/saldos/3.xlsx',
        '/Users/jetblack-work/Documents/Curve/arc/samples/1/saldos/4.xlsx',
        '/Users/jetblack-work/Documents/Curve/arc/samples/1/saldos/5.xlsx',
        '/Users/jetblack-work/Documents/Curve/arc/samples/1/saldos/6.xlsx',
        '/Users/jetblack-work/Documents/Curve/arc/samples/1/saldos/7.xlsx'
    ],
    'output-path': '/Users/jetblack-work/Desktop/output.xlsx',
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
