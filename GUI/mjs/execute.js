const fs = require('fs');
const rimraf = require('rimraf');
const unzipper = require('unzipper');
const settings = require('electron-settings');

const { spawn } = require('child_process');

const Dialog = require('./dialog');
const Window = require('./window');
const Path = require('./path');

class Execute {
    static runScript(args, input) {
        const errorWindow = new Window({
            width: 820,
            height: 700,
            minWidth: 400,
            minHeight: 600,
            show: false
        }, 'error.html', false);
        errorWindow.createWindow();

        const progressWindow = new Window({
            width: 820,
            height: 700,
            minWidth: 400,
            minHeight: 600
        }, 'progress.html', false);
        progressWindow.createWindow();

        return new Promise(resolve => {
            progressWindow.addWebListener('did-finish-load', () => {
                const subprocess = spawn('python', args);

                subprocess.stdin.write(JSON.stringify(input));
                subprocess.stdin.end();

                subprocess.stderr.on('data', err => {
                    errorWindow.show();
                    errorWindow.dispatchWebEvent('error', err.toString());
                });

                subprocess.stdout.on('data', data => {
                    progressWindow.dispatchWebEvent('progress', data.toString());
                });

                subprocess.on('close', () => {
                    if (settings.getSync('dataWindowClosesOnFinish')) {
                        progressWindow.window.close();
                    }
                    resolve(0);
                });
            });
        });
    }

    static attemptUpdate(packagePath) {
        return new Promise((resolve, reject) => {
            const extractionPath = Path.join(Path.appPaths.temp, 'arc_package');
            if (Path.exists(extractionPath)) {
                rimraf.sync(extractionPath);
            }

            Path.create(extractionPath);
            fs.createReadStream(packagePath).pipe(
                unzipper.Extract({ path: extractionPath })
            ).on('close', async () => {
                try {
                    const { packageName, requirements } = JSON.parse(
                        fs.readFileSync(
                            Path.join(extractionPath, 'dist', 'manifest.json')
                        )
                    );

                    const targetPath = Path.join(Path.appPaths.appData, 'Packages', packageName);

                    if (Path.exists(targetPath)) {
                        rimraf.sync(targetPath);
                    }

                    fs.renameSync(
                        Path.join(extractionPath, 'dist'),
                        targetPath
                    );

                    for (let i = 0; i < requirements.length; i++) {
                        await Execute.runScript([
                            '-m', 'pip', 'install', '--disable-pip-version-check', requirements[i]
                        ], '');
                    }

                    resolve();
                } catch (error) {
                    reject(error);
                }
            });
        });
    }

    static requestPackage() {
        const packagePath = Dialog.createOpenDialog([{ name: 'Arc Package', extensions: ['apf'] }]);

        if (packagePath) {
            return Execute.attemptUpdate(packagePath[0]);
        }
    }
}

module.exports = Execute;