class List {
    constructor(valuesContainer, properties) {
        this.valuesContainer = valuesContainer;

        this.id = properties.id;
        this.label = properties.label;
        this.inputs = properties.inputs;
        this.max = properties.max;

        this.seedTree();
    }

    seedTree() {
        this.DOMController = new ElementController(
            'DIV',
            {
                classList: new Set(['list-container'])
            }
        );

        this.listController = new ElementController(
            'DIV',
            {
                classList: new Set(['list-items-container'])
            }
        );
        this.DOMController.addChild(this.listController);

        const buttonController = new ElementController(
            'BUTTON',
            {
                text: this.label,
                classList: new Set(['add-button'])
            }
        );
        buttonController.addEventListener('click', () => {
            this.addRow();
        }, this);
        this.DOMController.addChild(buttonController);
    }

    addRow() {
        if (Object.values(this.listController.DOMTree.children).length < this.max) {
            const listRow = new ListRow(this.valuesContainer, this.id, this.inputs);
            this.listController.addChild(listRow.DOMController);
        }
    }
}