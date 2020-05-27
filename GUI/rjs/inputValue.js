class InputValue {
    constructor(content, type, setValidityClassCallback) {
        this.typeSystem = {
            int: /^\d[\d\.]*$/,
            float: /^(([\d\.]+,\d*)|(,?\d+))$/,
            percentage: /^((\d+\.\d*)|(\.?\d+))$/,
            dateString: /^(Jan|Fev|Mar|Abr|Mai|Jun|Jul|Ago|Set|Out|Nov|Dez)\/\d{4}$/,
            filePaths: 'size'
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