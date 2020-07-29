const { spawn } = require('child_process');

const subprocess = spawn('python', ['main.py']);

const input = {
    "arquivo-curva": "/Users/jetblack-work/Desktop/output.curve",
    'planilhas-saldo': [
        '/Users/jetblack-work/Documents/Curve/arc/samples/1/saldos/1.xlsx',
        '/Users/jetblack-work/Documents/Curve/arc/samples/1/saldos/2.xlsx',
        '/Users/jetblack-work/Documents/Curve/arc/samples/1/saldos/3.xlsx',
        '/Users/jetblack-work/Documents/Curve/arc/samples/1/saldos/4.xlsx',
        '/Users/jetblack-work/Documents/Curve/arc/samples/1/saldos/5.xlsx',
        '/Users/jetblack-work/Documents/Curve/arc/samples/1/saldos/6.xlsx',
        '/Users/jetblack-work/Documents/Curve/arc/samples/1/saldos/7.xlsx'
    ],
    'atual-saldo': { 16: [10_050_079], 17: [2_300_000] },
    'atual-juros': { 16: [70_000], 17: [60_000] },
    'atual-amort': { 16: [0], 17: [0] },
    'atual-amex': { 16: [100_000], 17: [40_000] },
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
