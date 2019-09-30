const { spawn } = require('child_process');

const subprocess = spawn('python3', ['arc.py']);

const input = {};
input['inputFiles'] = [
        'samples/1/saldos/1.xlsx',
        'samples/1/saldos/2.xlsx',
        'samples/1/saldos/3.xlsx',
        'samples/1/saldos/4.xlsx',
        'samples/1/saldos/5.xlsx',
        'samples/1/saldos/6.xlsx',
        'samples/1/saldos/7.xlsx',
];
input['outputFile'] = 'output.xlsx';
input['indexador'] = 0;
input['pu-emis'] = 1000;
input['total'] = 14270000;
input['r-sen'] = 80;
input['r-sub'] = 20;
input['mesostrata'] = [];
input['target-irr'] = 10.5;
input['t-em-senior-anual'] = 8.5;
input['c-period'] = 3;
input['fr-previsto'] = 400000;
input['pmt-proper'] = 75;
input['despesas'] = 10000;

//input['outputFile'] = 'output.xlsx';
//input['indexador'] = 0;
//input['pu-emis'] = 1000;
//input['total'] = 14270000;
//input['r-sen'] = 70;
//input['r-sub'] = 15;
//input['mesostrata'] = [['Mezanino', 15, 8.5]];
//input['target-irr'] = 10.5;
//input['t-em-senior-anual'] = 7;
//input['c-period'] = 3;
//input['fr-previsto'] = 400000;
//input['pmt-proper'] = 75;
//input['despesas'] = 10000;

subprocess.stdin.write(JSON.stringify(input));
subprocess.stdin.end();

subprocess.stderr.on('data', err => {
    console.log(err.toString());
});

subprocess.stdout.on('data', out => {
    console.log(out.toString());
});
