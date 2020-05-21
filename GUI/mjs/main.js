const {
    app,
    Menu,
    MenuItem
} = require('electron');

const Path = require('./path');
const Window = require('./window');
const Communication = require('./communication');
const Execute = require('./execute');

const menuTemplate = require('./menuTemplate');

Path.setup();
Communication.setDefault();

let mainWindow;
app.on('ready', () => {
    mainWindow = new Window({
        icon: '../assets/icon.png',
        frame: false,
        minWidth: 890,
        minHeight: 610,
        maxWidth: 1150,
        maxHeight: 770,
        fullscreen: false,
    }, 'index.html', true);
    mainWindow.createWindow();
});

app.on('window-all-closed', () => {
    if (isMac) {
        app.exit(0);
    }
});

app.on('activate', () => {
    if (mainWindow.isNull()) {
        mainWindow.createWindow();
    }
});

const menu = Menu.buildFromTemplate(menuTemplate);
Menu.setApplicationMenu(menu);
