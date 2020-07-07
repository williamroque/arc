class FileInputRow extends ElementController {
    constructor(valuesContainer, deleteCallback, path, inputID) {
        super(
            'DIV',
            {
                classList: new Set(['file-input-path-container'])
            }
        );

        this.valuesContainer = valuesContainer;
        this.deleteCallback = deleteCallback;

        this.path = path;
        this.inputID = inputID;

        this.seedTree();
    }

    getIndex() {
        let child = this.element, nodeIndex = 0;
        while ((child = child.previousSibling) !== null) {
            nodeIndex++;
        }

        return nodeIndex;
    }

    seedTree() {
        const pathText = new ElementController(
            'SPAN',
            {
                classList: new Set(['file-input-path-text']),
                text: this.path
            }
        );
        this.addChild(pathText);

        const deleteButton = new ElementController(
            'BUTTON',
            {
                classList: new Set(['icon', 'delete-button']),
                text: 'close'
            }
        );
        deleteButton.addEventListener('click', function(e) {
            this.deleteCallback(this.nodeID, this.path);
            this.remove();
        }, this);
        this.addChild(deleteButton);
    }
}