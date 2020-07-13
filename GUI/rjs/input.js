const { clipboard } = require('electron');

class Input extends ElementController {
    constructor(valuesContainer, properties, genericGroupID) {
        super(
            'DIV',
            {
                width: properties.width,
                classList: new Set(['form-cell'])
            }
        );

        this.valuesContainer = valuesContainer;

        this.id = properties.id;
        this.label = properties.label;
        this.group = properties.group;
        this.type = properties.type;

        this.genericGroupID = genericGroupID;

        this.seedTree();

        this.value = new InputValue('', this.type, this.setValidityClassCallback.bind(this));
    }

    seedTree() {
        const labelController = new ElementController(
            'LABEL',
            {
                text: this.label,
                classList: new Set(['form-input-label'])
            }
        );
        this.addChild(labelController, 'label');

        const inputController = new ElementController(
            'INPUT',
            {
                classList: new Set(['form-input'])
            }
        );
        inputController.addEventListener('keydown', this.handleKeyEvent, this);
        this.addChild(inputController, 'input');

        if (this.type === 'percentage') {
            const percentageLabelController = new ElementController(
                'LABEL',
                {
                    text: '%',
                    classList: new Set(['percentage-symbol'])
                }
            );
            this.addChild(percentageLabelController, 'percentageSymbol');
            inputController.addClass('percentage-input');
        }
    }

    setValidityClassCallback(isValid) {
        const inputNode = this.query('input');
        const labelNode = this.query('label');
        const percentageLabelNode = this.query('percentageSymbol');

        if (!isValid) {
            inputNode.addClass('form-input-invalid');
            labelNode.addClass('form-input-label-invalid');

            if (this.type === 'percentage') {
                percentageLabelNode.addClass('percentage-symbol-invalid');
            }
        } else {
            inputNode.removeClass('form-input-invalid');
            labelNode.removeClass('form-input-label-invalid');

            if (this.type === 'percentage') {
                percentageLabelNode.removeClass('percentage-symbol-invalid');
            }
        }
    }

    updateField(isDeletion, key) {
        const target = this.query('input').element;

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
            targetValue.splice(selStart, selEnd - selStart, key);
            targetValue = targetValue.join('');

            target.value = targetValue;
            target.setSelectionRange(selStart + 1, selStart + 1);
        }

        return targetValue;
    }

    updateFormValue(value) {
        const target = this.element;

        this.value.update(value);

        if (typeof this.genericGroupID !== 'undefined') {
            let nodeIndex = 0, child = target.parentNode;
            while ((child = child.previousSibling) !== null) {
                nodeIndex++;
            }

            this.valuesContainer.update(this.value, this.group, this.genericGroupID, nodeIndex);
        } else {
            this.valuesContainer.update(this.value, this.group, this.id);
        }
    }

    updateStyling() {
        const inputNode = this.query('input');
        const labelNode = this.query('label');
        const percentageLabelNode = this.query('percentageSymbol');

        if (this.value.content !== '') {
            inputNode.addClass('form-input-active');
            labelNode.addClass('form-input-label-active');

            if (this.type === 'percentage') {
                percentageLabelNode.addClass('percentage-symbol-active');
            }
        } else {
            inputNode.removeClass('form-input-active');
            labelNode.removeClass('form-input-label-active');

            if (this.type === 'percentage') {
                percentageLabelNode.removeClass('percentage-symbol-active');
            }
        }
    }

    handleKeyEvent(e) {
        if (e.key.length === 1 && !e.metaKey && !e.ctrlKey || e.key === 'Backspace') {
            this.updateFormValue(
                this.updateField(e.key === 'Backspace', e.key)
            );

            e.preventDefault();
        } else {
            if ((e.metaKey || e.ctrlKey) && e.key === 'v') {
                this.updateFormValue(
                    this.updateField(false, clipboard.readText())
                );
            } else if ((e.metaKey || e.ctrlKey) && e.key === 'x') {
                const target = this.query('input').element;

                const selStart = target.selectionStart;
                const selEnd = target.selectionEnd;
                clipboard.writeText(target.value.slice(selStart, selEnd));

                this.updateFormValue(
                    this.updateField(false, '')
                );
            }
        }
        this.updateStyling();
    }
}