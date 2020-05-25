class FileInput {
    constructor(valuesContainer, properties) {
        this.valuesContainer = valuesContainer;

        this.label = properties.label;
        this.allowedExtensions = properties.allowedExtensions
            .map(x => x.extensions)
            .flat();

        this.seedTree();
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
            this.DOMController.addClass('file-input-active');
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

            allowedFiles.forEach(file => {
                const pathContainer = new ElementController(
                    'DIV',
                    {
                        classList: new Set(['file-input-path-container'])
                    }
                );

                const pathText = new ElementController(
                    'SPAN',
                    {
                        classList: new Set(['file-input-path-text']),
                        text: file
                    }
                );
                pathContainer.addChild(pathText);

                this.DOMController.addChild(pathContainer);
            });

            this.DOMController.removeClass('file-input-active');
        }, this);

        this.DOMController.addEventListener('dragleave', e => {
            e.preventDefault();
            this.DOMController.removeClass('file-input-active');
        }, this);
    }
}