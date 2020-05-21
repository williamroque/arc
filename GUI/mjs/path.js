const { app } = require('electron');
const path = require('path');
const fs = require('fs');

class Path {
    static join() {
        return path.join(...arguments);
    }

    static get appPaths() {
        const appDataPath = app.getPath('userData');

        return {
            appData: appDataPath,
            packages: path.join(appDataPath, 'Packages'),
            logo: path.join(appDataPath, 'logos-logo.png')
        };
    }

    static get formSchemata() {
        const packageDirectories = fs
            .readdirSync(Path.appPaths.packages)
            .filter(path => !/^.*\..*$/.test(path));

        let forms = [];
        packageDirectories.forEach(directory => {
            const form = JSON.parse(
                fs.readFileSync(
                    Path.join(Path.appPaths.packages, directory, 'manifest.json')
                )
            );

            forms.push(form);
        });

        return forms;
    }

    static exists(path) {
        return fs.existsSync(path);
    }

    static create(path) {
        return fs.mkdirSync(path);
    }

    static setup() {
        const fixPath = require('fix-path');
        fixPath();

        if (!Path.exists(Path.appPaths.packages)) {
            Path.create(Path.appPaths.packages);
        }
    }
}

module.exports = Path;