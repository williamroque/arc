class List extends ElementController {
    constructor(valuesContainer, properties, syncedLists, data) {
        super(
            'DIV', {
                classList: new Set(['list-container'])
            }
        );

        this.valuesContainer = valuesContainer;

        this.id = properties.id;
        this.label = properties.label;
        this.inputs = properties.inputs;
        this.max = properties.max || Infinity;
        this.min = properties.min || 0;

        this.syncedLists = syncedLists || [this];

        this.data = data;

        this.showStateComplementLabel = 'Esconder';

        this.addEventListener('contextmenu', function (e) {
            const button = new ElementController(
                'BUTTON', {
                    classList: new Set(['toggle-button']),
                    'text': this.showStateComplementLabel
                }
            )

            button.addEventListener('click', function () {
                this.toggleListItemsVisibility();
            }, this);

            Toggle.show([button], e.pageX, e.pageY);
        }, this);

        this.listRows = [];
        this.incrementAnchors = {};

        this.seedTree();
    }

    calibrateIndices() {
        this.syncedLists.forEach(syncedList => {
            syncedList.incrementAnchors = this.incrementAnchors;
            syncedList.listRows.forEach((listRow, i) => {
                listRow.index = i;
            });
        });
    }

    deleteCallback(i, id) {
        if (this.listRows.length > this.min) {
            this.syncedLists.forEach(syncedList => {
                const listRow = syncedList.query('list-items-container').query(id);
                syncedList.listController.removeChild(id);
                syncedList.listRows.splice(i, 1);
                syncedList.calibrateIndices();

                listRow.delete.call(listRow);
            });
            this.calibrateIndices();
        }
    }

    seedTree() {
        this.listController = new ElementController(
            'DIV', {
                classList: new Set(['list-items-container'])
            }
        );
        this.addChild(this.listController, 'list-items-container');

        this.moreContainerController = new ElementController(
            'DIV', {
                classList: new Set(['more-container', 'hidden'])
            }
        );
        const moreController = new ElementController(
            'SPAN', {
                classList: new Set(['more']),
                text: '...'
            }
        );
        this.moreContainerController.addChild(moreController);
        this.moreContainerController.addEventListener('click', function () {
            this.toggleListItemsVisibility();
        }, this);
        this.addChild(this.moreContainerController);

        this.buttonController = new ElementController(
            'BUTTON', {
                text: this.label,
                classList: new Set(['add-button'])
            }
        );

        this.buttonController.addEventListener('click', function () {
            this.addRow();
        }, this);
        this.addChild(this.buttonController);

        while (this.listRows.length < this.min) {
            this.addRow();
        }
    }

    addRow(values) {
        if (Object.values(this.listController.DOMTree.children).length < this.max) {
            const listRow = new ListRow(this.valuesContainer, this.deleteCallback.bind(this), this.id, this.inputs, this.listRows.length, this.incrementAnchors, this.calibrateIndices.bind(this), this.data);
            this.listController.addChild(listRow);
            listRow.setFormValues(values);

            this.listRows.push(listRow);

            this.calibrateIndices();
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
