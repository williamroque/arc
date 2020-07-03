class Form extends ElementController {
    constructor(schema, container) {
        super(
            'DIV',
            {
                classList: new Set(['form'])
            }
        );

        this.schema = schema;
        this.container = container;

        this.valuesContainer = new ValuesContainer();

        this.seedTree();
    }

    seedTree() {
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

                    rowController.addChild(
                        inputCell,
                        (cellSchema.group ? `${cellSchema.group}=` : '') + cellSchema.id
                    );
                    inputCell.updateFormValue('');
                });
            } else if (rowSchema.type === 'list') {
                const list = new List(
                    this.valuesContainer,
                    rowSchema
                );

                rowController.addChild(list, rowSchema.id);
            } else if (rowSchema.type === 'file-input') {
                const fileInput = new FileInput(
                    this.valuesContainer,
                    rowSchema,
                    this
                );
                rowController.addChild(fileInput, rowSchema.id);
            }

            this.addChild(rowController);
        });
    }

    clearContainer() {
        let child;
        while (child = this.container.firstChild) {
            this.container.removeChild(child);
        }
    }

    activate() {
        this.clearContainer();
        this.container.appendChild(this.element);
    }
}