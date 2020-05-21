const {
    app,
    Menu
} = require('electron');

const Execute = require('./execute');

const Path = require('./path');
const Window = require('./window');
const Communication = require('./communication');

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

const isMac = process.platform === 'darwin';
const menuTemplate = [
    ...(isMac ? [{
        label: app.name,
        submenu: [
            { role: 'about' },
            { type: 'separator' },
            { role: 'hide' },
            { role: 'hideothers' },
            { role: 'unhide' },
            { type: 'separator' },
            {
                label: 'Quit',
                accelerator: 'Cmd+Q',
                click: () => app.exit(0)
            }
        ]
    }] : []),
    {
        label: 'Packages',
        submenu: [
            {
                label: 'Add Package',
                accelerator: 'CmdOrCtrl+Shift+P',
                click: () => Execute.requestPackage()
            },
            { type: 'separator' }
        ]
    },
    {
        label: 'Developer',
        submenu: [
            {
                label: 'Toggle Developer Tools',
                accelerator: 'Cmd+Alt+I',
                click: () => mainWindow.toggleDevTools()
            }
        ]
    }
];

const menu = Menu.buildFromTemplate(menuTemplate);
Menu.setApplicationMenu(menu);
