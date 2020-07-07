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

        this.showStateComplementLabel = 'Esconder';

        this.addEventListener('contextmenu', function (e) {
            const button = new ElementController(
                'BUTTON',
                {
                    classList: new Set(['toggle-button']),
                    'text': this.showStateComplementLabel
                }
            )

            button.addEventListener('click', function () {
                this.toggleListItemsVisibility();
            }, this);

            Toggle.show([button], e.pageX, e.pageY);
        }, this);

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

        this.moreContainerController = new ElementController(
            'DIV',
            {
                classList: new Set(['more-container', 'hidden'])
            }
        );
        const moreController = new ElementController(
            'SPAN',
            {
                classList: new Set(['more']),
                text: '...'
            }
        );
        this.moreContainerController.addChild(moreController);
        this.moreContainerController.addEventListener('click', function() {
            this.toggleListItemsVisibility();
        }, this);
        this.addChild(this.moreContainerController);

        const buttonController = new ElementController(
            'BUTTON',
            {
                text: this.label,
                classList: new Set(['add-button'])
            }
        );

        buttonController.addEventListener('click', function() {
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

    toggleListItemsVisibility() {
        if (this.showStateComplementLabel === 'Esconder') {
            this.listController.addClass('hidden');
            this.moreContainerController.removeClass('hidden');

            this.showStateComplementLabel = 'Mostrar';
        } else {
            this.listController.removeClass('hidden');
            this.moreContainerController.addClass('hidden');

            this.showStateComplementLabel = 'Esconder';
        }
    }
}