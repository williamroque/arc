class ListRow extends ElementController {
    constructor(valuesContainer, deleteCallback, listID, inputSchemata, index, incrementAnchors, calibrateIndicesCallback) {
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
                this.incrementInputs[cellSchema.incrementGroup] = inputCell;
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
            this.delete();
            this.deleteCallback(this._index, this.nodeID);
        }, this);
        this.addChild(deleteButton);
    }

    setFormValues(values) {
        this.inputs.forEach((input, i) => {
            if (typeof values !== 'undefined') {
                formattedNum = values[i].toString();
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

    setAnchor(group, anchor) {
        this.incrementAnchors[group] = anchor;
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
