const {
    app,
    dialog,
    ipcMain
} = require('electron');

const fs = require('fs');
const path = require('path');

const windowStateKeeper = require('electron-window-state');

const appData = app.getPath('appData');

const shell = require('shelljs');
const nShell = require('electron').shell;

const appDataPath = app.getPath('userData');
const scriptPath = path.join(app.getPath('userData'), 'Script');
const formPath = path.join(app.getPath('userData'), 'Forms');

const Window = require('./window');

let configErrorScheduled = true;

if (
    fs.existsSync(path.join(scriptPath, 'arc.py')) &&
    fs.readdirSync(formPath).some(f => /\.json$/.test(f))
) {
    configErrorScheduled = false;
}

const fixPath = require('fix-path');
fixPath();

function writeData(data, path) {
    fs.writeFile(path, data, err => {
        console.log(err);
    });
}

function readData(path) {
    let data;
    try  {
        data = fs.readFileSync(path);
    } catch (_) {
        data = '{}';
    }
    return data;
}

function runScript(args) {
    return new Promise(resolve => {
        if (!shell.which('python3')) {
            console.log('Python 3 not installed');
            resolve(1);
        }

        const spawn = require('child_process').spawn;
        const process = spawn('python3', args);

        process.stdout.on('error', err => {
            console.log('Error:', err);
        });

        process.on('exit', () => {
            resolve(0);
        });
    });
}

const createSelectDialog = () => dialog.showOpenDialog({
    properties: ['openFile', 'multiSelections'],
    filters: [
        { name: 'Excel', extensions: ['xls', 'xlsx'] }
    ]
});

const createSaveDialog = () => dialog.showSaveDialog({
    properties: ['openFile'],
    filters: [
        { name: 'Excel', extensions: ['xlsx'] }
    ]
});

ipcMain.on('get-forms', (event, _) => {
    event.returnValue = fs.readdirSync(formPath)
        .filter(f => /\.json$/.test(f))
        .map(form => {
            const formObj = JSON.parse(readData(path.join(formPath, form)));
            return formObj;
        });
});

ipcMain.on('get-open-dialog', (event, _) => {
    event.returnValue = createSelectDialog();
});

ipcMain.on('run-script', async (event, path) => {
    const fileName = createOpenDialog();

    let returnCode = 0;

    if (fileName && !configErrorScheduled) {
        returnCode = await runScript(false, [path.join(scriptPath, 'arc.py'), path, fileName]);
    }

    event.returnValue = returnCode;
});

ipcMain.on('attempt-update', async (event, path) => {
    const packageData = JSON.parse(readData(path));

    if (packageData.hasOwnProperty('script')) {
        writeData(JSON.stringify(packageData.script), path.join(scriptPath, 'arc.py'));
    }

    if (packageData.hasOwnProperty('forms')) {
        packageData.forms.forEach(form => {
            writeData(JSON.stringify(form), form.id + '.json');
        });
    }

    event.returnValue = 1;
});

const mainWinObject = {
    center: true,
    icon: '../assets/icon.png',
    frame: false,
    minWidth: 890,
    minHeight: 610,
    maxWidth: 1150,
    maxHeight: 770,
    fullscreen: false,
};

let mainWin;

const createWindow = () => {
    let mainWindowState = windowStateKeeper({
        defaultWidth: 1150,
        defaultHeight: 750
    });

    mainWinObject.width = mainWindowState.width;
    mainWinObject.height = mainWindowState.height;

    mainWin = new Window(mainWinObject);
    
    if (configErrorScheduled) {
        dialog.showMessageBox(null, {
            message: 'Configuration not set.',
        });
    }

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

