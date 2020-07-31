const {
    app,
    Menu,
    shell
} = require('electron');
const settings = require('electron-settings');

const Execute = require('./execute');

const Path = require('./path');
const Window = require('./window');
const Communication = require('./communication');
const Dialog = require('./dialog');

const isMac = process.platform === 'darwin';

Path.setup();
Communication.setDefault();

const settingsSchemata = [
    {
        type: 'header',
        title: 'Janela'
    },
    {
        type: 'setting',
        id: 'dataWindowClosesOnFinish',
        label: 'Fechar janela de dados ao completar proceso',
        inputType: 'checkbox',
        defaultValue: true
    },
    {
        type: 'header',
        title: 'Formulário'
    },
    {
        type: 'setting',
        id: 'useDecimalDot',
        label: 'Usar ponto em vez de vírgula como separador decimal',
        inputType: 'checkbox',
        defaultValue: false
    }
];

for (const schema of settingsSchemata) {
    if (schema.type === 'setting') {
        if (!settings.hasSync(schema.id)) {
            settings.setSync(schema.id, schema.defaultValue);
        }
    }
}

const preferencesWindow = new Window(
    {
        width: 400,
        height: 500,
        defaultWidth: 400,
        defaultHeight: 500
    },
    'preferences.html',
    false,
    ['render', settingsSchemata]
);

let mainWindow;
app.on('ready', () => {
    mainWindow = new Window({
        icon: '../assets/icon.png',
        frame: false,
        minWidth: 890,
        minHeight: 610,
        maxWidth: 1150,
        maxHeight: 770,
        fullscreen: false
    }, 'index.html', true);
    mainWindow.createWindow();
});

app.on('window-all-closed', () => {
    app.exit(0);
});

app.on('activate', () => {
    if (mainWindow.isNull()) {
        mainWindow.createWindow();
    }
});

let selectedPackageIndex;
const menuTemplate = [
    ...(isMac ? [{
        label: app.name,
        submenu: [{
                role: 'about'
            },
            {
                type: 'separator'
            },
            {
                label: 'Configurações',
                accelerator: 'CmdOrCtrl+,',
                click: () => {
                    if (preferencesWindow.isNull()) {
                        preferencesWindow.createWindow();
                        preferencesWindow.dispatchWebEvent('render', settingsSchemata);
                    } else {
                        preferencesWindow.window.close();
                    }
                }
            },
            {
                type: 'separator'
            },
            {
                role: 'hide'
            },
            {
                role: 'hideothers'
            },
            {
                role: 'unhide'
            },
            {
                role: 'close'
            },
            {
                type: 'separator'
            },
            {
                label: 'Quit',
                accelerator: 'Cmd+Q',
                click: () => app.exit(0)
            }
        ]
    }] : []),
    {
        label: 'Edit',
        submenu: [
            { role: 'undo' },
            { role: 'redo' },
            { type: 'separator' },
            {
                label: 'Cut',
                accelerator: 'CmdOrCtrl+X'
            },
            { role: 'copy' },
            {
                label: 'Paste',
                accelerator: 'CmdOrCtrl+V'
            },
            { type: 'separator' },
            { role: 'selectAll' }
        ]
    },
    {
        label: 'Packages',
        submenu: [{
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
            {
                label: 'Next Package',
                accelerator: 'CmdOrCtrl+Shift+N',
                click: () => {
                    const schemata = Path.formSchemata;
                    selectedPackageIndex = (selectedPackageIndex + 1) % schemata.length  || 0;

                    selectPackage(schemata[selectedPackageIndex].packageName);
                }
            },
            {
                type: 'separator'
            },
            ...Path.formSchemata.map((form, i) => {
                if (form.isDefault) {
                    selectedPackageIndex = i;
                }

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
    {
        role: 'windowMenu'
    },
    {
        label: 'Developer',
        submenu: [{
            label: 'Toggle Developer Tools',
            accelerator: 'Cmd+Alt+I',
            click: () => mainWindow.toggleDevTools()
        }]
    },
    {
        label: 'Help',
        role: 'help',
        submenu: [{
                type: 'separator'
            },
            {
                label: 'Relatar problema',
                click: () => shell.openExternal(
                    `mailto:william.roque@ethosgroup.com.br?subject=Arc@${app.getVersion()}%20Issue`
                )
            }
        ]
    }
];

const menu = Menu.buildFromTemplate(menuTemplate);
Menu.setApplicationMenu(menu);

function selectPackage(packageID) {
    menu.getMenuItemById(packageID).checked = true;
    mainWindow.dispatchWebEvent('update-form', packageID);
}