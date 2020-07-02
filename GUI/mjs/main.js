const {
    app,
    Menu,
    MenuItem
} = require('electron');

const Execute = require('./execute');

const Path = require('./path');
const Window = require('./window');
const Communication = require('./communication');
const Dialog = require('./dialog');

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
                    Execute.requestPackage().then(() => {
                        if (Dialog.ask('Reiniciar?')) {
                            app.relaunch();
                            app.exit();
                        }
                    });
                }
            },
            { type: 'separator' },
            ...Path.formSchemata.map(form => {
                return {
                    label: form.title,
                    type: 'radio',
                    checked: form.isDefault,
                    id: form.packageName,
                    click: item => {
                        mainWindow.dispatchWebEvent('update-form', item.id);
                    }
                }
            })
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