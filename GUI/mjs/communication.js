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
            const scriptPath = Path.join(Path.appPaths.packages, currentPackage.packageName, 'main.py');
            if (!Path.exists(scriptPath)) {
                Dialog.showError('Package Error', 'Package contents missing or corrupted.');
                event.returnValue = 'error';

                return;
            }


            input['output-path'] = Dialog.createSaveDialog(currentPackage.allowedOutputExtensions);
            if (!input['output-path']) {
                event.returnValue = false;

                return;
            }

            event.returnValue = await Execute.runScript([scriptPath], input);
        });
    }
}

module.exports = Communication;