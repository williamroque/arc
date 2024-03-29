const { ipcRenderer } = require('electron');

class Communication {
    static requestFormSchemata() {
        return ipcRenderer.sendSync('get-form-schemata');
    }

    static requestSaveDialog() {
        return ipcRenderer.sendSync('get-save-dialog');
    }

    static requestRunScript(input, currentPackage) {
        return ipcRenderer.sendSync('run-script', input, currentPackage);
    }

    static addListener(event, callback) {
        ipcRenderer.on(event, callback);
    }
}
