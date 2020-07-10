class ListRow extends ElementController {
    constructor(valuesContainer, deleteCallback, listID, inputSchemata) {
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

        this.inputs = [];

        this.seedTree();
    }

    delete() {
        let nodeIndex = 0, child = this.element;
        while ((child = child.previousSibling) !== null) {
            nodeIndex++;
        }

        for (const cellSchema of this.inputSchemata) {
            this.valuesContainer.removeAtIndex(cellSchema.group, this.listID, nodeIndex);
        }
    }

    seedTree() {
        for (const cellSchema of this.inputSchemata) {
            const inputCell = new Input(
                this.valuesContainer,
                cellSchema,
                this.listID
            );
            this.addChild(inputCell);

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
            this.deleteCallback(this.nodeID);
        }, this);
        this.addChild(deleteButton);
    }

    setFormValues(values) {
        this.inputs.forEach((input, i) => {
            if (typeof values !== 'undefined') {
                input.query('input').element.value = new Intl.NumberFormat('pt-BR').format(values[i]);
                input.updateFormValue(values[i]);
                input.updateStyling();
            } else {
                input.updateFormValue('');
            }
        });
    }
}
