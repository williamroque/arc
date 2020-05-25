class ListRow {
    constructor(valuesContainer, listID, inputs) {
        this.valuesContainer = valuesContainer;
        this.listID = listID;
        this.inputs = inputs;

        this.seedTree();
    }

    seedTree() {
        this.DOMController = new ElementController(
            'DIV',
            {
                classList: new Set(['form-row'])
            }
        );

        this.inputs.forEach(cellSchema => {
            const inputCell = new Input(
                this.valuesContainer,
                cellSchema,
                this.listID
            );

            this.DOMController.addChild(inputCell.DOMController);
        });

        const deleteButton = new ElementController(
            'BUTTON',
            {
                classList: new Set(['icon', 'delete-list-row-button']),
                text: 'close'
            }
        );
        deleteButton.addEventListener('click', () => {
            this.DOMController.remove();

            let nodeIndex = 0, child = this.DOMController.element;
            while ((child = child.previousSibling) !== null) {
                nodeIndex++;
            }

            this.inputs.forEach(cellSchema => {
                this.valuesContainer.removeAtIndex(cellSchema.group, this.listID, nodeIndex);
            });
        }, this);
        this.DOMController.addChild(deleteButton);
    }
}