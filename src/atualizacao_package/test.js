const { spawn } = require('child_process');

const subprocess = spawn('python', ['main.py']);

const input = {
    'arquivo-curva': ['/Users/jetblack-work/Desktop/output.curve'],
    'planilhas-saldo': ['/Users/jetblack-work/Desktop/saldo_atual.xlsx'],
    'ipca-periodo': { 'ipca': ['2019', '2020', '2021', '2022'] },
    'ipca-anual': { 'ipca': [0, 0, 0, 0] },
    'atual-data': { '16': ['out/2019', 'out/2019', 'nov/2019', 'dez/2019'], '17': ['set/2019', 'out/2019', 'nov/2019', 'dez/2019'] },
    'atual-juros': { '16': [78_000, 79_000, 80_000, 81_000, 82_000, 83_000], '17': [60_000, 61_000, 62_000, 63_000, 64_000, 65_000] },
    'atual-amort': { '16': [0, 0, 0, 100_000, 99_000, 98_000], '17': [0, 0, 0, 0, 0, 0] },
    'atual-amex': { '16': [0, 0, 0, 50000, 60_000, 100_000], '17': [0, 0, 0, 25000, 0, 0] },
    'atual-pu': { '16': [7_700, 7_702, 7_704, 7_706, 7_708, 7_710], '17': [1_990, 1_992, 1_994, 1_996, 1_998, 2_000] },
    'atual-quantidade': { '16': [1_500, 1_500, 1_500, 1_500, 1_500, 1_500], '17': [1_500, 1_500, 1_500, 1_500, 1_500, 1_500] },
    'output-path': '/Users/jetblack-work/Desktop/output.xlsx'
};


subprocess.stdin.write(JSON.stringify(input));
subprocess.stdin.end();

subprocess.stderr.on('data', err => {
    console.log(err.toString());
});

subprocess.stdout.on('data', out => {
    console.log(out.toString());
});
