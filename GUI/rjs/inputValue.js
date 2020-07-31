const settings = require('electron-settings');

class InputValue {
    constructor(content, type, setValidityClassCallback) {
        const floatPattern = settings.getSync('useDecimalDot') ?
            /^\d[\d,]*(\.\d+)?$/ :
            /^\d[\d\.]*(,\d+)?$/;
        const datePattern = /^(Jan|Fev|Mar|Abr|Mai|Jun|Jul|Ago|Set|Out|Nov|Dez)\/\d{4}$/i;

        this.typeSystem = {
            int: /^\d[\d\.]*$/,
            float: floatPattern,
            percentage: floatPattern,
            dateString: datePattern,
            filePaths: 'size',
            anualIncrement: /^\d{4}$/,
            monthlyIncrement: datePattern
        };

        this.content = content;

        if (type in this.typeSystem) {
            this.type = type;
            this.typeValid = this.typeSystem[type];
        } else {
            throw new Error(`Unknown type '${type}'.`);
        }

        this.setValidityClassCallback = setValidityClassCallback;
    }

    update(value) {
        this.content = value;
    }

    test() {
        if (typeof this.typeValid === 'string') {
            return !!this.content[this.typeValid];
        } else {
            return this.typeValid.test(this.content);
        }
    }
}