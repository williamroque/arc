const fs = require('fs');
const rimraf = require('rimraf');

const { spawn } = require('child_process');

const Dialog = require('./dialog');
const Window = require('./window');
const Path = require('./path');

class Execute {
    static runScript(scriptPath, input) {
        const errorWindow = new Window({
            width: 820,
            height: 700,
            minWidth: 400,
            minHeight: 600,
            show: false
        }, 'error.html', false);

        const progressWindow = new Window({
            width: 820,
            height: 700,
            minWidth: 400,
            minHeight: 600
        }, 'progress.html', false);

        return new Promise(resolve => {
            progressWindow.addWebListener('did-finish-load', () => {
                const subprocess = spawn('python3', [scriptPath]);

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
                    resolve(0);
                });
            });
        });
    }

    static attemptUpdate(packagePath) {
        // Binary image data has to be "decoded" as latin1 to be included in the package header
        let [logoImg, packageData] = fs.readFileSync(packagePath).toString('latin1').split('|===|');
        packageData = JSON.parse(packageData);

        try {
            const packageTargetPath = Path.join(Path.appPaths.packages, packageData.manifest.packageName);
            if (fs.existsSync(packageTargetPath)) {
                rimraf.sync(packageTargetPath);
            }

            fs.mkdirSync(packageTargetPath);
            packageData.scripts.forEach(script => {
                fs.writeFileSync(Path.join(Path.appPaths.packages, packageData.manifest.packageName, script.path), script.contents);
            });
            fs.writeFileSync(
                Path.join(Path.appPaths.packages, packageData.manifest.packageName, 'manifest.json'),
                JSON.stringify(packageData.manifest)
            );

            fs.writeFileSync(Path.appPaths.logo, Buffer.from(logoImg, 'latin1'));

            return 'success';
        } catch (error) {
            return error;
        }
    }

    static requestPackage() {
        const packagePath = Dialog.createOpenDialog([{ name: 'Arc Package', extensions: ['apf'] }]);

        if (packagePath) {
            return Execute.attemptUpdate(packagePath[0]);
        }
    }
}

module.exports = Execute;