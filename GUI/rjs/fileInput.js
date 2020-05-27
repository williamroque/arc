class FileInput {
    constructor(valuesContainer, properties) {
        this.valuesContainer = valuesContainer;

        this.label = properties.label;
        this.id = properties.id;
        this.allowedExtensions = properties.allowedExtensions
            .map(x => x.extensions)
            .flat();

        this.fileCount = 0;

        this.seedTree();

        this.files = new Set();

        this.value = new InputValue(this.files, 'filePaths', this.setValidityClassCallback.bind(this));
        this.valuesContainer.update(this.value, null, this.id);
    }

    seedTree() {
        this.DOMController = new ElementController(
            'DIV',
            {
                text: this.label,
                classList: new Set(['file-input'])
            }
        );

        this.DOMController.addEventListener('dragover', e => {
            e.preventDefault();
            this.DOMController.addClass('file-input-drag');
        }, this);

        this.DOMController.addEventListener('drop', e => {
            e.preventDefault();

            let allowedFiles = [];
            Array.from(e.dataTransfer.files).forEach(file => {
                const filePattern = /^.+\.([a-z]{1,4})$/;

                const [path, extension] = file.path.match(filePattern);

                if (this.allowedExtensions.indexOf(extension) > -1) {
                    allowedFiles.push(path);
                }
            });

            if (this.fileCount === 0 && allowedFiles.length > 0) {
                this.DOMController.toggleText();
                this.DOMController.addClass('file-input-active');
            }

            allowedFiles.forEach(file => {
                this.fileCount++;

                const fileInputRow = new FileInputRow(
                    this.valuesContainer,
                    this.deleteCallback.bind(this),
                    file,
                    this.id
                );
                this.DOMController.addChild(fileInputRow.DOMController);

                this.files.add(file);
                this.value.update(this.files);

                this.valuesContainer.update(this.value, null, this.id);
            });

            this.DOMController.removeClass('file-input-drag');
        }, this);

        this.DOMController.addEventListener('dragleave', e => {
            e.preventDefault();
            this.DOMController.removeClass('file-input-drag');
        }, this);
    }

    deleteCallback(id, path) {
        this.files.delete(path);

        if (--this.fileCount < 1) {
            this.DOMController.toggleText();
            this.DOMController.removeClass('file-input-active');
        }
        this.DOMController.removeChild(id);
    }

    setValidityClassCallback(isValid) {
        if (!isValid) {
            this.DOMController.addClass('file-input-invalid');
        } else {
            this.DOMController.removeClass('file-input-invalid');
        }
    }
}