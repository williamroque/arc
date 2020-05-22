class ListRow {
    constructor(updateValueCallback, listID, inputs) {
        this.updateValueCallback = updateValueCallback;
        this.listID = listID;
        this.inputs = inputs;

        this.seedTree();
    }

    updateValue(group, _, value, nodeIndex) {
        this.updateValueCallback(group, this.listID, value, nodeIndex);
    }

    seedTree() {
        this.DOMController = new ElementController(
            'DIV',
            {
                classList: ['form-row']
            }
        );

        this.inputs.forEach(cellSchema => {
            const inputCell = new Input(
                this.updateValue.bind(this),
                cellSchema,
                true
            );

            this.DOMController.addChild(inputCell.DOMController);
        });
    }
}