const { dialog } = require('electron');

class Dialog {
    static createSaveDialog(filters) {
        return dialog.showSaveDialogSync({
            properties: ['openFile'],
            filters: filters
        })
    }

    static createOpenDialog(filters) {
        return dialog.showOpenDialogSync({
            properties: ['openFile'],
            filters: filters
        });
    }

    static showError(title, content) {
        dialog.showErrorBox(title, content);
    }
}

module.exports = Dialog;