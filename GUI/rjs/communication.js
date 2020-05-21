const { ipcRenderer } = require('electron');

class Communication {
    static requestFormSchemata() {
        return ipcRenderer.sendSync('get-form-schemata');
    }

    static requestSaveDialog() {
        return ipcRenderer.sendSync('get-save-dialog');
    }

    static requestRunScript(input, currentForm) {
        return ipcRenderer.sendSync('run-script', input, currentPackage);
    }

    static requestAttemptUpdate(path) {
        return ipcRenderer.sendSync('attempt-update', path);
    }
}