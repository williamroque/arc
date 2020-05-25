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

        console.log(this.values);
    }

    removeAtIndex(group = NaN, id = NaN, index = NaN) {
        if (group in this.values) {
            if (id in this.values[group]) {
                this.values[group][id].splice(index, 1);
            }
        }

        console.log(this.values);
    }
}