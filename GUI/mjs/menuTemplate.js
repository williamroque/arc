const { app } = require('electron');

const isMac = process.platform === 'darwin';

module.exports = [
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