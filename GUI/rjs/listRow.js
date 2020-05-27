class ListRow {
    constructor(valuesContainer, deleteCallback, listID, inputSchemata) {
        this.valuesContainer = valuesContainer;
        this.deleteCallback = deleteCallback;

        this.listID = listID;
        this.inputSchemata = inputSchemata;

        this.inputs = [];

        this.seedTree();
    }

    seedTree() {
        this.DOMController = new ElementController(
            'DIV',
            {
                classList: new Set(['form-row'])
            }
        );

        this.inputSchemata.forEach(cellSchema => {
            const inputCell = new Input(
                this.valuesContainer,
                cellSchema,
                this.listID
            );

            this.DOMController.addChild(inputCell.DOMController);

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
            let nodeIndex = 0, child = this.DOMController.element;
            while ((child = child.previousSibling) !== null) {
                nodeIndex++;
            }

            this.inputSchemata.forEach(cellSchema => {
                this.valuesContainer.removeAtIndex(cellSchema.group, this.listID, nodeIndex);
            });

            this.deleteCallback(this.DOMController.nodeID);
            this.DOMController.remove();
        }, this);
        this.DOMController.addChild(deleteButton);
    }

    setFormValues() {
        this.inputs.forEach(input => {
            input.updateFormValue('');
        });
    }
}