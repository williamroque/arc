class ValuesContainer {
    constructor() {
        this.values = {};
    }

    update(value, group, id, index) {
        if (group) {
            if (!(group in this.values)) {
                this.values[group] = {};
            }

            if (!(id in this.values[group])) {
                this.values[group][id] = [];
            }

            if (typeof index !== 'undefined') {
                this.values[group][id][index] = value;
            } else {
                this.values[group][id] = value;
            }
        } else {
            if (!(id in this.values)) {
                this.values[id] = [];
            }

            if (typeof index !== 'undefined') {
                this.values[id][index] = value;
            } else {
                this.values[id] = value;
            }
        }
    }

    removeAtIndex(group, id, index) {
        if (group && group in this.values) {
            if (
                id in this.values[group] &&
                Array.isArray(this.values[group][id])
            ) {
                this.values[group][id].splice(index, 1);
            }
        } else {
            if (
                id in this.values &&
                Array.isArray(this.values[id])
            ) {
                this.values[id].splice(index, 1);
            }
        }
    }

    areAllValid(obj = this.values) {
        let areValid = true;

        Object.values(obj).forEach(value => {
            if (value instanceof InputValue) {
                const isValid = value.test();

                if (!isValid) {
                    areValid = false;
                }
                value.setValidityClassCallback(isValid);
            } else if (typeof value === 'object' && value !== null) {
                if (!this.areAllValid(value)) {
                    areValid = false;
                }
            }
        });

        return areValid;
    }

    clean(value) {
        if (settings.getSync('useDecimalDot')) {
            value = value.replace(/,/g, '');
        } else {
            value = value.replace(/\./g, '');
            value = value.replace(/,/g, '.')
        }

        return value
            .replace(/\s/g, '')
            .replace(/-/g, '/');
    }

    cast(inputValue) {
        if (inputValue.type === 'filePaths') {
            return Array.from(inputValue.content);
        }

        const content = this.clean(inputValue.content);
        switch (inputValue.type) {
            case 'int':
                return parseInt(content);
            case 'float':
                return parseFloat(content);
            case 'percentage':
                return parseFloat(content) / 100;
            default:
                return content;
        }
    }

    parse(obj = this.values) {
        return Object.fromEntries(Object.entries(obj).map(([key, value]) => {
            if (value instanceof InputValue) {
                return [key, this.cast(value)];
            } else if (Array.isArray(value)) {
                return [key, Object.values(this.parse(value))];
            } else {
                return [key, this.parse(value)];
            }
        }));
    }
}