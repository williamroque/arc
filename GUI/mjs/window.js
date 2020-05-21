const { BrowserWindow } = require('electron');
const windowStateKeeper = require('electron-window-state');

const url = require('url');

const Path = require('./path');

class Window {
    constructor(properties, file, keepsState) {
        this.properties = properties;
        this.file = file;

        this.properties.webPreferences = { nodeIntegration: true };

        if (keepsState) {
            this.windowState = windowStateKeeper({
                defaultWidth: 1150,
                defaultHeight: 750
            });

            this.properties.width = this.windowState.width;
            this.properties.height = this.windowState.height;
        }
    }

    createWindow() {
        this.window = new BrowserWindow(this.properties);
        this.window.loadURL(url.format({
            pathname: Path.join(__dirname, `../html/${this.file}`),
            protocol: 'file:',
            slashes: true
        }));

        if (this.windowState) {
            this.windowState.manage(this.window);
        }

        this.addListener('closed', e => this.window = null);
    }

    show() {
        this.window.show();
    }

    isNull() {
        return this.window === null;
    }

    addListener(event, callback) {
        this.window.on(event, callback);
    }

    addWebListener(event, callback) {
        this.window.webContents.once(event, callback);
    }

    dispatchWebEvent(event, message) {
        this.window.webContents.send(event, message);
    }

    toggleDevTools() {
        this.window.webContents.toggleDevTools();
    }
}

module.exports = Window;
