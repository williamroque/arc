const fs = require('fs');
const {
    dialog
} = require('electron').remote;

class FileInput extends ElementController {
    constructor(valuesContainer, properties, parentNode) {
        super(
            'DIV', {
                text: properties.label,
                classList: new Set(['file-input'])
            }
        );

        this.valuesContainer = valuesContainer;
        this.parentNode = parentNode;

        this.properties = properties;

        this.id = properties.id;
        this.max = properties.max || Infinity;
        this.readToRows = properties.readToRows;
        this.allowedExtensions = properties.allowedExtensions
            .map(x => x.extensions)
            .flat();

        this.seedTree();

        this.fileCount = 0;
        this.files = new Set();

        this.value = new InputValue(this.files, 'filePaths', this.setValidityClassCallback.bind(this));
        this.valuesContainer.update(this.value, null, this.id);
    }

    addFile(file) {
        if (this.fileCount === 0) {
            this.toggleText();
            this.addClass('file-input-active');
        }

        this.fileCount++;

        const fileInputRow = new FileInputRow(
            this.valuesContainer,
            this.deleteCallback.bind(this),
            file,
            this.id
        );
        this.addChild(fileInputRow);

        if (typeof this.readToRows !== 'undefined') {
            const data = JSON.parse(fs.readFileSync(file));

            this.lists = [];

            Object.entries(data[this.readToRows.drawFrom]).forEach(([serie, rows]) => {
                const rowController = new ElementController(
                    'DIV', {
                        classList: new Set(['form-row'])
                    }
                );

                const rowSchema = JSON.parse(JSON.stringify(this.readToRows));
                rowSchema.label = rowSchema.label.replace('{}', serie);
                rowSchema.id = rowSchema.id.replace('{}', serie);

                const list = new List(
                    this.valuesContainer,
                    rowSchema,
                    this.lists,
                    data
                );

                if (this.readToRows.sync) {
                    list.buttonController.addEventListener('click', function (e) {
                        for (const list of this.lists) {
                            if (list.element !== e.currentTarget.parentNode) {
                                list.addRow();
                            }
                        }
                    }, this);
                }

                this.lists.push(list);

                rowController.addChild(
                    list,
                    rowSchema.id
                );
                this.parentNode.addChild(rowController);

                for (const row of rows) {
                    list.addRow(row);
                }
            });
        }

        this.files.add(file);
        this.value.update(this.files);

        this.valuesContainer.update(this.value, null, this.id);
    }

    seedTree() {
        this.addEventListener('click', function (e) {
            const files = dialog.showOpenDialogSync({
                properties: ['openFile', 'multiSelections'],
                filters: this.properties.allowedExtensions
            });

            if (files) {
                files.forEach(file => {
                    if (this.files.size + 1 <= this.max) {
                        this.addFile(file);
                    }
                });
            }
        }, this);

        this.addEventListener('dragover', function (e) {
            e.preventDefault();
            this.addClass('file-input-drag');
        }, this);

        this.addEventListener('drop', function (e) {
            e.preventDefault();

            let allowedFiles = [];
            for (const file of Array.from(e.dataTransfer.files)) {
                const filePattern = /^.+\.([a-z]+)$/;

                const [path, extension] = file.path.match(filePattern);

                if (this.allowedExtensions.indexOf(extension) > -1) {
                    allowedFiles.push(path);
                }
            }

            if (this.files.size + allowedFiles.length > this.max) {
                allowedFiles = allowedFiles.slice(0, this.max - this.files.size);
            }

            for (const file of allowedFiles) {
                this.addFile(file);
            }

            this.removeClass('file-input-drag');
        }, this);

        this.addEventListener('dragleave', function (e) {
            e.preventDefault();
            this.removeClass('file-input-drag');
        }, this);
    }

    deleteCallback(id, path) {
        this.files.delete(path);

        if (--this.fileCount < 1) {
            this.toggleText();
            this.removeClass('file-input-active');
        }
        this.removeChild(id);
    }

    setValidityClassCallback(isValid) {
        if (!isValid) {
            this.addClass('file-input-invalid');
        } else {
            this.removeClass('file-input-invalid');
        }
    }
}