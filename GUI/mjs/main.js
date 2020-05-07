const {
    app,
    dialog,
    ipcMain
} = require('electron');

const fs = require('fs');
const path = require('path');

const windowStateKeeper = require('electron-window-state');

const { spawn } = require('child_process');

const appData = app.getPath('userData');
const scriptPath = path.join(appData, 'Script');
const formPath = path.join(appData, 'Forms');
const logoPath = path.join(appData, 'logos-logo.png')

const Window = require('./window');

const fixPath = require('fix-path');
fixPath();

if (!fs.existsSync(scriptPath)) {
    fs.mkdirSync(scriptPath);
}

if (!fs.existsSync(formPath)) {
    fs.mkdirSync(formPath);
}

let errorWin;
let progressWin;
function runScript(input) {
    errorWin = new Window({
        width: 820,
        height: 700,
        minWidth: 400,
        minHeight: 600,
        show: false,
        webPreferences: {
            nodeIntegration: true
        }
    }, 'error.html');

    progressWin = new Window({
        width: 820,
        height: 700,
        minWidth: 400,
        minHeight: 600,
        webPreferences: {
            nodeIntegration: true
        }
    }, 'progress.html');

    return new Promise(resolve => {
        progressWin.window.webContents.once('did-finish-load', () => {
            const subprocess = spawn('python3', [path.join(scriptPath, 'main.py')]);

            subprocess.stdin.write(input);
            subprocess.stdin.end();

            subprocess.stderr.on('data', err => {
                errorWin.window.show();
                errorWin.window.webContents.send('error', err.toString());
            });

            subprocess.stdout.on('data', data => {
                progressWin.window.webContents.send('progress', data.toString());
            });

            subprocess.on('close', () => {
                resolve(0);
            });
        });
    });
}

const createSaveDialog = () => dialog.showSaveDialogSync({
    properties: ['openFile'],
    filters: [
        { name: 'Excel', extensions: ['xlsx'] }
    ]
});

function requestPackage() {
    const packagePath = dialog.showOpenDialogSync({
        properties: ['openFile'],
        filters: [
            { name: 'Arc Package', extensions: ['apf'] }
        ]
    })[0];

    if (packagePath) {
        attemptUpdate(packagePath);
    }
}

ipcMain.on('get-save-dialog', (event, _) => {
    event.returnValue = createSaveDialog();
});

ipcMain.on('run-script', async (event, input) => {
    while (!fs.existsSync(`${scriptPath}/main.py`)) {
        requestPackage();
    }

    let returnCode = 0;
    returnCode = await runScript(JSON.stringify({...input, cwd: process.cwd()}));

    event.returnValue = returnCode;
});

function attemptUpdate(path) {
    let [ logoImg, packageData ] = fs.readFileSync(path).toString('latin1').split('|===|');
    packageData = JSON.parse(packageData);

    Object.keys(packageData).forEach(script => {
        fs.writeFileSync(`${scriptPath}/${script}`, packageData[script]);
    });

    fs.writeFileSync(logoPath, Buffer.from(logoImg, 'latin1'));

    return 0;
}

ipcMain.on('attempt-update', (event, path) => {
    event.returnValue = attemptUpdate(path);
});

const mainWinObject = {
    icon: '../assets/icon.png',
    frame: false,
    minWidth: 890,
    minHeight: 610,
    maxWidth: 1150,
    maxHeight: 770,
    fullscreen: false,
    webPreferences: {
        nodeIntegration: true
    }
};

let mainWin;

const createWindow = () => {
    let mainWindowState = windowStateKeeper({
        defaultWidth: 1150,
        defaultHeight: 750
    });

    mainWinObject.width = mainWindowState.width;
    mainWinObject.height = mainWindowState.height;

    mainWin = new Window(mainWinObject, 'index.html');

    mainWindowState.manage(mainWin.window);
};

app.on('ready', createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.exit(0);
    }
});

app.on('activate', () => {
    if (!mainWin || mainWin.window === null) {
        mainWin = createWindow();
    }
});

