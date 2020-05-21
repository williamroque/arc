class Form {
    constructor(schema, container) {
        this.schema = schema;
        this.container = container;

        this.values = {};

        this.seedTree();
    }

    updateValue(group, id, value) {
        if (group) {
            this.values[group][id] = value;
        } else {
            this.values[id] = value;
        }
    }

    seedTree() {
        this.DOMController = new ElementController(
            'DIV',
            {
                classList: new Set(['form'])
            }
        );

        this.schema.form.forEach(rowSchema => {
            const rowController = new ElementController(
                'DIV',
                {
                    classList: new Set(['form-row'])
                }
            );

            if (rowSchema.type === 'input-row') {
                rowSchema.inputs.forEach(cellSchema => {
                    const inputCell = new Input(
                        this.updateValue.bind(this),
                        cellSchema
                    );

                    rowController.addChild(inputCell.DOMController);
                });
            } else if (rowSchema.type === 'list') {
                const buttonController = new ElementController(
                    'BUTTON',
                    {
                        text: rowSchema.label,
                        classList: new Set(['add-button'])
                    }
                );
                rowController.addChild(buttonController);
            } else if (rowSchema.type === 'file-input') {
                const fileInputController = new ElementController(
                    'DIV',
                    {
                        text: rowSchema.label,
                        classList: new Set(['file-input'])
                    }
                );
                rowController.addChild(fileInputController);
            }

            this.DOMController.addChild(rowController);
        });
    }

    clearContainer() {
        let child;
        while (child = this.container.firstChild) {
            this.container.removeChild(child);
        }
    }

    render() {
        this.clearContainer();
        this.container.appendChild(this.DOMController.element);
    }
}




// document.body.addEventListener('dragover', e => {
//     e.preventDefault();

//     document.body.classList.add('drag-overlay');
// }, false);

// document.body.addEventListener('drop', e => {
//     e.preventDefault();
//     e.stopPropagation();

//     let files = {};
//     Array.from(e.dataTransfer.files).forEach(file => {
//         const filePattern = /^(?:\w|\/|\\|:)+\.([a-z]{1,4})$/;

//         if (filePattern.test(file)) {
//             const [path, extension] = file.match(filePattern);

//             if (extension in files) {
//                 files[extension].push(path);
//             } else {
//                 files[extension] = [path];
//             }
//         }
//     });

//     currentForm.schema.fileInputs.forEach(inputType => {
//         const { extension } = inputType;

//         if (extension in files) {
//             fileInputContainer.classList.add('file-input-occupied');
            
//         }
//     });
//     // CHANGE
//     if (inputFiles.length < 1 && files.length) {
//         clearNode(fileContainer);

//         fileContainer.classList.add('file-input-occupied');
//         fileList = document.createElement('UL');
//         fileList.setAttribute('id', 'file-list');

//         fileContainer.appendChild(fileList);
//     } else {
//         fileList = document.querySelector('#file-list');
//     }

//     // ADD FILES AS LIST NODES TO FILES PROMPT
//     // DO NOT ADD FILES ALREADY PRESENT
//     // FILES HAVE CLASS file-node
//     // DELETE BUTTONS HAVE CLASS delete-node-button

//     document.body.classList.remove('drag-overlay');
// }, false);

// document.body.addEventListener('dragleave', e => {
//     e.preventDefault();

//     document.body.classList.remove('drag-overlay');
// }, false);