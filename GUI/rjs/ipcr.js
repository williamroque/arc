const { ipcRenderer } = require('electron');

function requestForms() {
    return ipcRenderer.sendSync('get-forms');
}

function requestSaveDialog() {
    return ipcRenderer.sendSync('get-save-dialog');
}

function requestRunScript(input) {
    return ipcRenderer.sendSync('run-script', input);
}

function requestAttemptUpdate(path) {
    return ipcRenderer.sendSync('attempt-update', path);
}
