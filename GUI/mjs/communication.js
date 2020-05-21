const { ipcMain } = require('electron');
const fs = require('fs');

const Dialog = require('./dialog');
const Path = require('./path');
const Execute = require('./execute');

class Communication {
    static setDefault() {
        ipcMain.on('get-form-schemata', event => {
            event.returnValue = Path.formSchemata;
        });

        ipcMain.on('get-save-dialog', event => {
            event.returnValue = Dialog.createSaveDialog();
        });

        ipcMain.on('run-script', async (event, input, currentPackage) => {
            const scriptPath = Path.join(Path.appPaths.packages, currentPackage, 'main.py');
            while (!Path.exists(scriptPath)) {
                Execute.requestPackage();
            }

            input['appdata-path'] = Path.appPaths.appData;

            event.returnValue = await Execute.runScript(scriptPath, input);
        });

        ipcMain.on('attempt-update', (event, path) => {
            event.returnValue = Execute.attemptUpdate(path);
        });
    }
}

module.exports = Communication;