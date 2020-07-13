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
    'atual-saldo': { 16: [3453, 2155, 5312], 17: [5326, 3214, 4523], 18: [8839, 2349, 2393] },
    'atual-juros': { 16: [9823, 1234, 3249], 17: [1000, 1234, 2356], 18: [1248, 3298, 1749] },
    'atual-amort': { 16: [8123, 4321, 1244], 17: [1234, 2315, 2346], 18: [3291, 3892, 1048] },
    'atual-amex': { 16: [9784, 9827, 0], 17: [5678, 9487, 6243], 18: [1938, 1734, 1983] },
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
