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

    seedTree() {
        this.inputSchemata.forEach(cellSchema => {
            const inputCell = new Input(
                this.valuesContainer,
                cellSchema,
                this.listID
            );
            this.addChild(inputCell);

            this.inputs.push(inputCell);
        });

        const deleteButton = new ElementController(
            'BUTTON',
            {
                classList: new Set(['icon', 'delete-button']),
                text: 'close'
            }
        );
        deleteButton.addEventListener('click', () => {
            let nodeIndex = 0, child = this.element;
            while ((child = child.previousSibling) !== null) {
                nodeIndex++;
            }

            this.inputSchemata.forEach(cellSchema => {
                this.valuesContainer.removeAtIndex(cellSchema.group, this.listID, nodeIndex);
            });

            this.deleteCallback(this.nodeID);
            this.remove();
        }, this);
        this.addChild(deleteButton);
    }

    setFormValues(values = Array(this.inputs.length).fill('')) {
        this.inputs.forEach((input, i) => {
            input.query('input').element.value = new Intl.NumberFormat('pt-BR').format(values[i]);
            input.updateFormValue(values[i]);
            input.updateStyling();
        });
    }
}