class ListRow extends ElementController {
    constructor(valuesContainer, deleteCallback, listID, inputSchemata, index, incrementAnchors, calibrateIndicesCallback, data) {
        super(
            'DIV',
            {
                classList: new Set(['form-row'])
            }
        );

        this.valuesContainer = valuesContainer;
        this.deleteCallback = deleteCallback;

        this.listID = listID;
        this.inputSchemata = inputSchemata;

        this._index = index;
        this.incrementAnchors = incrementAnchors;
        this.calibrateIndicesCallback = calibrateIndicesCallback;

        this.data = data;

        this.inputs = [];
        this.incrementInputs = {};

        this.seedTree();
    }

    delete() {
        for (const cellSchema of this.inputSchemata) {
            this.valuesContainer.removeAtIndex(cellSchema.group, this.listID, this._index);
        }
    }

    seedTree() {
        for (const cellSchema of this.inputSchemata) {
            const inputCell = new Input(
                this.valuesContainer,
                cellSchema,
                this.listID,
                this.setAnchor.bind(this),
                (function() { return this._index }).bind(this)
            );
            this.addChild(inputCell);

            if ('incrementGroup' in cellSchema) {
                const group = cellSchema.incrementGroup;

                if ('drawDefault' in cellSchema) {
                    this.setAnchor(group, this.addToDate(this.data[cellSchema.drawDefault], cellSchema.initialOffset), cellSchema.type);
                }

                this.incrementInputs[group] = inputCell;
            }

            this.inputs.push(inputCell);
        }

        const deleteButton = new ElementController(
            'BUTTON',
            {
                classList: new Set(['icon', 'delete-button']),
                text: 'close'
            }
        );
        deleteButton.addEventListener('click', function() {
            this.deleteCallback(this._index, this.nodeID);
        }, this);
        this.addChild(deleteButton);
    }

    setFormValues(values) {
        this.inputs.forEach((input, i) => {
            if (typeof values !== 'undefined') {
                let formattedNum = values[i].toString();
                if ((input.type === 'float' || input.type === 'percentage') && settings.getSync('useDecimalDot')) {
                    formattedNum = values[i].replace(/\./g, ',');
                }

                input.query('input').element.value = formattedNum;
                input.updateFormValue(values[i]);
                input.updateStyling();
            } else {
                input.updateFormValue('');
            }
        });
    }

    addToDate(date, i) {
        const MONTHS = 'Jan|Fev|Mar|Abr|Mai|Jun|Jul|Ago|Set|Out|Nov|Dez'.split('|').map(m => m.toLowerCase());
        let [month, year] = date.split('/');

        const monthIndex = MONTHS.indexOf(month.toLowerCase());

        year |= 0;
        if (i < 0) {
            year -= Math.ceil(-((monthIndex + i) / 12));
        } else {
            year += (monthIndex + i) / 12 | 0;
        }

        month = MONTHS[(12 + monthIndex + i % 12) % 12];

        return `${month}/${year}`;

    }

    setAnchor(group, date, type) {
        if (type === 'anualIncrement') {
            this.incrementAnchors[group] = {
                anchor: (parseInt(date) - this._index).toString(),
                getDisplacement: function (i) {
                    return (parseInt(this.anchor) + i).toString();
                }
            };
        } else if (type === 'monthlyIncrement') {
            this.incrementAnchors[group] = {
                anchor: this.addToDate(date, -this._index),
                getDisplacement: (function (i) {
                    return this.addToDate(date, i);
                }).bind(this)
            };
        }
        this.calibrateIndicesCallback();
    }

    set index(i) {
        this._index = i;

        Object.entries(this.incrementInputs).forEach(([group, input]) => {
            if (group in this.incrementAnchors) {
                input.setFieldValue(
                    this.incrementAnchors[group].getDisplacement(i)
                );
            }
        });
    }
}
