const {
    app,
    dialog,
    ipcMain
} = require('electron');

const fs = require('fs');
const path = require('path');

const windowStateKeeper = require('electron-window-state');

const appData = app.getPath('appData');

const { spawn } = require('child_process');

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

function runScript(input) {
    const subprocess = spawn('python3', [path.join(scriptPath, 'arc.py')]);

    subprocess.stdin.write(input);
    subprocess.stdin.end();

    subprocess.stderr.on('data', err => {
        console.log(err.toString());
    });

    return new Promise(resolve => {
        subprocess.on('close', () => {
            resolve(0);
        });
    });
}

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

ipcMain.on('get-save-dialog', (event, _) => {
    event.returnValue = createSaveDialog();
});

ipcMain.on('run-script', async (event, input) => {
    let returnCode = 0;
    if (!configErrorScheduled) {
        returnCode = await runScript(JSON.stringify(input));
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

    event.returnValue = 0;
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

