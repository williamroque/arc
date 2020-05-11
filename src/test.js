const { spawn } = require('child_process');

const subprocess = spawn('python3', ['main.py']);

const input = {};
input['inputFiles'] = [
    '../samples/1/saldos/1.xlsx',
    '../samples/1/saldos/2.xlsx',
    '../samples/1/saldos/3.xlsx',
    '../samples/1/saldos/4.xlsx',
    '../samples/1/saldos/5.xlsx',
    '../samples/1/saldos/6.xlsx',
    '../samples/1/saldos/7.xlsx',
];

input['outputFile'] = 'output.xlsx';
input['indexador'] = 0;
input['pu-emis'] = 1000;
input['total'] = 14270000;
input['razoes'] = [15, 15, 70]
input['target-irr'] = 10.5;
input['taxas-juros'] = [8.5, 7];
input['c-period'] = 3;
input['fr-previsto'] = 400000;
input['pmt-proper'] = 92;
input['despesas'] = 10000;
input['starting-date'] = 'Set/2019';
input['appdata-path'] = '/Users/jetblack-work/Library/Application Support/Arc';

subprocess.stdin.write(JSON.stringify(input));
subprocess.stdin.end();

subprocess.stderr.on('data', err => {
    console.log(err.toString());
});

subprocess.stdout.on('data', out => {
    console.log(out.toString());
});
