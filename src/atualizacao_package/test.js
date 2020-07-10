const { spawn } = require('child_process');

const subprocess = spawn('python3', ['main.py']);

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
    'atual-juros': { 16: [9823, 1234], 17: [1000, 1234, 2356], 18: [] },
    'atual-amort': { 16: [8123, 4321], 17: [1234, 2315, 2346], 18: [] },
    'atual-amex': { 16: [9784, 9827], 17: [5678, 9487, 6243], 18: [] },
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
