const settings = require('electron-settings');

class InputValue {
    constructor(content, type, setValidityClassCallback) {
        const testFloat = s => settings.getSync('useDecimalDot') ?
            /^\d[\d,]*(\.\d+)?$/.test(s.trim()) :
            /^\d[\d\.]*(,\d+)?$/.test(s.trim());
        const datePattern = /^(Jan|Fev|Mar|Abr|Mai|Jun|Jul|Ago|Set|Out|Nov|Dez)\/\d{4}$/i;

        this.typeSystem = {
            int: s => /^\d[\d\.]*$/.test(s.trim()),
            float: testFloat,
            percentage: testFloat,
            percentageOptional: s => s.trim() === '' || testFloat(s.trim()),
            dateString: s => datePattern.test(s.trim()),
            filePaths: s => this.content.size > 0,
            anualIncrement: s => /^\d{4}$/.test(s.trim()),
            monthlyIncrement: s => datePattern.test(s.trim())
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
        return this.typeValid(this.content);
    }
}