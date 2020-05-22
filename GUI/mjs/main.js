const {
    app,
    Menu
} = require('electron');

const Execute = require('./execute');

const Path = require('./path');
const Window = require('./window');
const Communication = require('./communication');

const isMac = process.platform === 'darwin';

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
    if (!isMac) {
        app.exit(0);
    }
});

app.on('activate', () => {
    if (mainWindow.isNull()) {
        mainWindow.createWindow();
    }
});

const menuTemplate = [
    ...(isMac ? [{
        label: app.name,
        submenu: [
            { role: 'about' },
            { type: 'separator' },
            { role: 'hide' },
            { role: 'hideothers' },
            { role: 'unhide' },
            { role: 'close' },
            { type: 'separator' },
            {
                label: 'Quit',
                accelerator: 'Cmd+Q',
                click: () => app.exit(0)
            }
        ]
    }] : []),
    { role: 'editMenu' },
    {
        label: 'Packages',
        submenu: [
            {
                label: 'Add Package',
                accelerator: 'CmdOrCtrl+Shift+P',
                click: () => {
                    const package = Execute.requestPackage();

                    if (package === 'success') {
                        mainWindow.dispatchWebEvent('update-form-schemata', Path.formSchemata);
                    }
                }
            },
            { type: 'separator' }
        ]
    },
    { role: 'windowMenu' },
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
