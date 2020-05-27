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

    areAllValid(obj=this.values) {
        Object.values(obj).forEach(value => {
            if (value instanceof InputValue) {
                value.setValidityClassCallback(value.test());
            } else if (typeof value === 'string') {
                
            } else if (typeof value === 'object' && value !== null) {
                this.areAllValid(value);
            } 
        });
    }
}