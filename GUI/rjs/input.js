class Input {
    constructor(updateValueCallback, properties) {
        this.updateValueCallback = updateValueCallback;

        this.id = properties.id;
        this.label = properties.label;
        this.width = properties.width;
        this.group = properties.group;

        this.value = new InputValue('', properties.type);

        this.seedTree();
        this.DOMController.element.addEventListener(
            'keyup',
            this.handleKeyEvent.bind(this),
            false,
        )
    }

    seedTree() {
        this.DOMController = new ElementController(
            'DIV',
            {
                width: this.width,
                classList: new Set(['form-cell'])
            }
        );

        const labelController = new ElementController(
            'LABEL',
            {
                text: this.label,
                classList: new Set(['form-input-label'])
            }
        );
        this.DOMController.addChild(labelController, 'label');

        const inputController = new ElementController(
            'INPUT',
            {
                classList: new Set(['form-input'])
            }
        );
        this.DOMController.addChild(inputController, 'input');

        if (this.value.type === 'percentage') {
            const percentageLabelController = new ElementController(
                'LABEL',
                {
                    text: '%',
                    classList: new Set(['percentage-symbol'])
                }
            );
            this.DOMController.addChild(percentageLabelController, 'percentageSymbol');
        }
    }

    handleKeyEvent(e) {
        const target = e.currentTarget;

        this.value.update(target.value);
        this.updateValueCallback(this.group, this.id, this.value);

        const labelNode = this.DOMController.getChild('label');
        const percentageLabelNode = this.DOMController.getChild('percentageSymbol');

        if (this.value.content) {
            labelNode.addClass('text-input-label-active');

            if (this.value.type === 'percentage') {
                percentageLabelNode.addClass('perc-symbol-active');
            }
        } else {
            labelNode.removeClass('text-input-label-active');

            if (this.value.type === 'percentage') {
                percentageLabelNode.removeClass('perc-symbol-active');
            }
        }
    }
}