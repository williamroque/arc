const {
    app,
    dialog,
    ipcMain
} = require('electron');

const fs = require('fs');
const path = require('path');


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
}




function attemptUpdate(path) {
}


const mainWinObject = {
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
