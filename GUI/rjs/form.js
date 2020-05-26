class Form {
    constructor(schema, container) {
        this.schema = schema;
        this.container = container;

        this.valuesContainer = new ValuesContainer();

        this.seedTree();
    }

    seedTree() {
        this.DOMController = new ElementController(
            'DIV',
            {
                classList: new Set(['form'])
            }
        );

        this.schema.form.forEach(rowSchema => {
            const rowController = new ElementController(
                'DIV',
                {
                    classList: new Set(['form-row'])
                }
            );

            if (rowSchema.type === 'input-row') {
                rowSchema.inputs.forEach(cellSchema => {
                    const inputCell = new Input(
                        this.valuesContainer,
                        cellSchema
                    );

                    rowController.addChild(inputCell.DOMController);
                });
            } else if (rowSchema.type === 'list') {
                const list = new List(
                    this.valuesContainer,
                    rowSchema
                );

                rowController.addChild(list.DOMController);
            } else if (rowSchema.type === 'file-input') {
                const fileInput = new FileInput(
                    this.valuesContainer,
                    rowSchema
                );
                rowController.addChild(fileInput.DOMController);
            }

            this.DOMController.addChild(rowController);
        });
    }

    clearContainer() {
        let child;
        while (child = this.container.firstChild) {
            this.container.removeChild(child);
        }
    }

    render() {
        this.clearContainer();
        this.container.appendChild(this.DOMController.element);
    }
}