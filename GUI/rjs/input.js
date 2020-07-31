const { clipboard } = require('electron');

class Input extends ElementController {
    constructor(valuesContainer, properties, genericGroupID, setAnchorCallback, getIndex) {
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
        this.incrementGroup = properties.incrementGroup;

        this.genericGroupID = genericGroupID;

        this.setAnchorCallback = setAnchorCallback;
        this.getIndex = getIndex;

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

        const selLength = selEnd - selStart;

        let targetValue;

        if (isDeletion) {
            let cursorOffset = 0;

            if (selLength > 0) {
                targetValue = this.setFieldValue('', [selStart, selEnd]);
            } else {
                targetValue = this.setFieldValue('', [selStart - 1, selEnd]);
                cursorOffset = 1;
            }

            target.setSelectionRange(selStart - cursorOffset, selStart - cursorOffset);
        } else {
            targetValue = this.setFieldValue(key, [selStart, selEnd]);
            target.setSelectionRange(selStart + 1, selStart + 1);
        }

        if (this.type === 'anualIncrement') {
            if (this.value.test()) {
                this.setAnchorCallback(
                    this.incrementGroup,
                    {
                        anchor: (parseInt(targetValue) - this.getIndex()).toString(),
                        getDisplacement: function (i) {
                            return (parseInt(this.anchor) + i).toString();
                        }
                    }
                );
            }
        } else if (this.type === 'monthlyIncrement') {
            if (this.value.test()) {
                this.setAnchorCallback(
                    this.incrementGroup,
                    {
                        anchor: this.addToDate(targetValue, -this.getIndex()),
                        getDisplacement: (function (i) {
                            return this.addToDate(targetValue, i - this.getIndex());
                        }).bind(this)
                    }
                );
            }
        }

        return targetValue;
    }

    setFieldValue(value, range=[0, value.length]) {
        const target = this.query('input').element;
        let targetValue = target.value.split('');

        targetValue.splice(range[0], range[1] - range[0], value);
        targetValue = targetValue.join('');

        target.value = targetValue;

        this.updateFormValue(targetValue);

        return targetValue;
    }

    addToDate(date, i) {
        const MONTHS = 'Jan|Fev|Mar|Abr|Mai|Jun|Jul|Ago|Set|Out|Nov|Dez'.split('|').map(m => m.toLowerCase());
        let [month, year] = date.split('/');

        const monthIndex = MONTHS.indexOf(month.toLowerCase());

        year |= 0;
        if (i < 0) {
            year -= Math.ceil(-((monthIndex + i) / 12));
        } else {
            year += (monthIndex + i) / 12 | 0;
        }

        month = MONTHS[(12 + monthIndex + i % 12) % 12];

        return `${month}/${year}`;

    }

    updateFormValue(value) {
        this.value.update(value);

        if (this.type !== 'anualIncrement' && this.type !== 'monthlyIncrement') {
            if (typeof this.genericGroupID !== 'undefined') {
                this.valuesContainer.update(this.value, this.group, this.genericGroupID, this.getIndex());
            } else {
                this.valuesContainer.update(this.value, this.group, this.id);
            }
        }

        this.updateStyling();
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
            this.updateField(e.key === 'Backspace', e.key)

            e.preventDefault();
        } else {
            if ((e.metaKey || e.ctrlKey) && e.key === 'v') {
                this.updateField(false, clipboard.readText())
            } else if ((e.metaKey || e.ctrlKey) && e.key === 'x') {
                const target = this.query('input').element;

                const selStart = target.selectionStart;
                const selEnd = target.selectionEnd;
                clipboard.writeText(target.value.slice(selStart, selEnd));

                this.updateField(false, '')
            }
        }
    }
}