const { BrowserWindow } = require('electron');
const path = require('path');
const url = require('url');

class Window {
    constructor(winObject, file) {
        this.window = new BrowserWindow(winObject);
        this.loadURL(file);
        this.window.on('closed', e => this.window = null);
    }

    loadURL(file) {
        this.window.loadURL(url.format({
            pathname: path.join(__dirname, `../html/${file}`),
            protocol: 'file:',
            slashes: true
        }));
    }
}

module.exports = Window;
