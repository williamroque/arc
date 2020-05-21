class InputValue {
    constructor(content, type) {
        this.typeSystem = {
            int: /^\d[\d\.]*$/,
            float: /^(([\d\.]+,\d*)|(,?\d+))$/,
            percentage: /^((\d+\.\d*)|(\.?\d+))$/,
            dateString: /^(Jan|Fev|Mar|Abr|Mai|Jun|Jul|Ago|Set|Out|Nov|Dez)\/\d{4}$/
        };

        this.content = content;

        if (type in this.typeSystem) {
            this.type = type;
            this.typeValid = this.typeSystem[type];
        } else {
            throw new Error(`Unknown type '${type}'.`);
        }
    }

    update(value) {
        this.content = value;
    }

    test() {
        return this.typeValid.test(this.content);
    }
}