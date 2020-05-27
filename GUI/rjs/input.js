class Input {
    constructor(valuesContainer, properties, genericGroupID) {
        this.valuesContainer = valuesContainer;

        this.id = properties.id;
        this.label = properties.label;
        this.width = properties.width;
        this.group = properties.group;

        this.genericGroupID = genericGroupID;

        this.value = new InputValue('', properties.type);

        this.seedTree();
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
        inputController.addEventListener('keydown', this.handleKeyEvent, this);
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
            inputController.addClass('percentage-input');
        }
    }

    updateField(isDeletion, e) {
        const target = e.currentTarget;

        const selStart = target.selectionStart;
        const selEnd = target.selectionEnd;

        let targetValue = target.value.split('');

        const selLength = selEnd - selStart;
        if (isDeletion) {
            let cursorOffset = 0;
            if (selLength > 0) {
                targetValue.splice(selStart, selLength);
            } else {
                targetValue.splice(selStart - 1, 1);
                cursorOffset = 1;
            }
            targetValue = targetValue.join('');

            target.value = targetValue;
            target.setSelectionRange(selStart - cursorOffset, selStart - cursorOffset);
        } else {
            targetValue.splice(selStart, selEnd - selStart, e.key);
            targetValue = targetValue.join('');

            target.value = targetValue;
            target.setSelectionRange(selStart + 1, selStart + 1);
        }

        return targetValue;
    }

    updateFormValue(value) {
        this.value.update(value);

        if (typeof this.genericGroupID !== 'undefined') {
            let nodeIndex = 0, child = target.parentNode.parentNode;
            while ((child = child.previousSibling) !== null) {
                nodeIndex++;
            }

            this.valuesContainer.update(this.value.content, this.group, this.genericGroupID, nodeIndex);
        } else {
            this.valuesContainer.update(this.value.content, this.group, this.id);
        }
    }

    updateStyling() {
        const inputNode = this.DOMController.getChild('input');
        const labelNode = this.DOMController.getChild('label');
        const percentageLabelNode = this.DOMController.getChild('percentageSymbol');

        if (this.value.content) {
            inputNode.addClass('form-input-active');
            labelNode.addClass('form-input-label-active');

            if (this.value.type === 'percentage') {
                percentageLabelNode.addClass('percentage-symbol-active');
            }
        } else {
            inputNode.removeClass('form-input-active');
            labelNode.removeClass('form-input-label-active');

            if (this.value.type === 'percentage') {
                percentageLabelNode.removeClass('percentage-symbol-active');
            }
        }
    }

    handleKeyEvent(e) {
        if (e.key.length === 1 && !e.metaKey && !e.ctrlKey || e.key === 'Backspace') {
            this.updateFormValue(
                this.updateField(e.key === 'Backspace', e)
            );

            e.preventDefault();
        }

        this.updateStyling();
    }
}