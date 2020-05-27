class FileInputRow {
    constructor(valuesContainer, deleteCallback, path, inputID) {
        this.valuesContainer = valuesContainer;
        this.deleteCallback = deleteCallback;

        this.path = path;
        this.inputID = inputID;

        this.seedTree();
    }

    getIndex() {
        let child = this.DOMController.element, nodeIndex = 0;
        while ((child = child.previousSibling) !== null) {
            nodeIndex++;
        }

        return nodeIndex;
    }

    seedTree() {
        this.DOMController = new ElementController(
            'DIV',
            {
                classList: new Set(['file-input-path-container'])
            }
        );

        const pathText = new ElementController(
            'SPAN',
            {
                classList: new Set(['file-input-path-text']),
                text: this.path
            }
        );
        this.DOMController.addChild(pathText);

        const deleteButton = new ElementController(
            'BUTTON',
            {
                classList: new Set(['icon', 'delete-button']),
                text: 'close'
            }
        );
        deleteButton.addEventListener('click', e => {
            this.deleteCallback(this.DOMController.nodeID, this.path);
            this.DOMController.remove();
        }, this);
        this.DOMController.addChild(deleteButton);
    }
}