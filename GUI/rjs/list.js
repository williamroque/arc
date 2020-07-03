class List extends ElementController {
    constructor(valuesContainer, properties) {
        super(
            'DIV',
            {
                classList: new Set(['list-container'])
            }
        );

        this.valuesContainer = valuesContainer;

        this.id = properties.id;
        this.label = properties.label;
        this.inputs = properties.inputs;
        this.max = properties.max || Infinity;

        this.seedTree();
    }

    deleteCallback(id) {
        this.listController.removeChild(id);
    }

    seedTree() {
        this.listController = new ElementController(
            'DIV',
            {
                classList: new Set(['list-items-container'])
            }
        );
        this.addChild(this.listController);

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
        this.addChild(buttonController);
    }

    addRow(values) {
        if (Object.values(this.listController.DOMTree.children).length < this.max) {
            const listRow = new ListRow(this.valuesContainer, this.deleteCallback.bind(this), this.id, this.inputs);
            this.listController.addChild(listRow);
            listRow.setFormValues(values);
        }
    }
}