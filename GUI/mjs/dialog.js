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
}

module.exports = Dialog;