const formContainer = document.querySelector('#form-container');
const fileContainer = document.querySelector('#file-container');

const messagePrompt = document.querySelector('#message-prompt');

const buildButton = document.querySelector('build');

const forms = requestForms();
let currentForm = forms.find(f => f.id === 'basic') || forms[0];

let inputFiles = [];

function clearNode(elem) {
    let first;
    while (first = elem.firstChild) first.remove();
}

let promptTimeout;

function showPrompt(message, period) {
    if (promptTimeout) {
        clearTimeout(promptTimeout);
    }

    clearNode(messagePrompt);
    messagePrompt.innerHTML = `<p>${message}</p>`;

    messagePrompt.classList.add('prompt-visible');

    promptTimeout = setTimeout(() => {
        messagePrompt.classList.remove('prompt-visible');
    }, period);
}

function catalyzeBuild() {
    let values = [];

    formContainer.childNodes.forEach(row => {
        row.childNodes.forEach(col => {
            const input = col.childNodes[1];
            values.push([
                input.value,
                input.getAttribute('data-type'),
                col.childNodes[0].innerText,
                input.id
            ]);
        });
    });

    const firstInvalid = values.find(v => !finalRegEx[v[1]].test(v[0]));
    if (firstInvalid) {
        showPrompt(`Valor inválido no campo <b>${firstInvalid[2].toLowerCase()}</b>.`, 2000);
    } else {
        if (inputFiles.length) {
            let inputs = {};
            values.forEach(value => {
                inputs[value[3]] = value[0];
            });
            inputs.inputFiles = inputFiles;
            inputs.outputFile = requestSaveDialog();

            requestRunScript(inputs);
        }
    }
}

function renderForm(form) {
    clearNode(formContainer);

    form.form.forEach(row => {
        const formRow = document.createElement('DIV');
        formRow.classList.add('form-row');
        
        row.forEach(col => {
            const formCol = document.createElement('DIV');
            formCol.classList.add('form-col');

            const { id, label, type, width } = col;

            const input = document.createElement('INPUT');

            input.setAttribute('data-type', type);

            if (
                type === 'percentage' ||
                type === 'float' ||
                type === 'int'
            ) {
                input.setAttribute('type', 'text');

                if (type === 'percentage') {
                    input.classList.add('percentage-input');
                } else {
                    input.classList.add('standard-input');
                }
                
                const inputLabel = document.createElement('LABEL');
                inputLabel.classList.add('text-input-label')
                inputLabel.setAttribute('for', id);
                inputLabel.innerText = label;

                formCol.appendChild(inputLabel);

                input.addEventListener('keydown', e => {
                    const target = e.currentTarget;
                    const type = target.getAttribute('data-type');

                    const labelElem = target.parentNode.firstChild;
                    const pSymElem = target.parentNode.childNodes[2];

                    if (e.key === 'Enter') {
                        catalyzeBuild();
                    } else if (e.key.length < 2) {
                        e.preventDefault();

                        const value = target.value + e.key;
                        if (
                            type === 'int' && /^\d+$/.test(value) ||
                            /^((\d*\.\d+)|(\d+\.?))$/.test(value)
                        ) {
                            target.value += e.key;
                        }
                    }

                    if (target.value) {
                        labelElem.classList.add('text-input-label-active');

                        if (type === 'percentage') {
                            pSymElem.classList.add('perc-symbol-active');
                        }
                    } else {
                        labelElem.classList.remove('text-input-label-active');

                        if (type === 'percentage') {
                            pSymElem.classList.remove('perc-symbol-active');
                        }
                    }
                }, false);
            } 

            input.setAttribute('id', id);
            formCol.style.width = `${width}%`;

            formCol.appendChild(input);

            if (type === 'percentage') {
                const pSymElem = document.createElement('LABEL');
                pSymElem.classList.add('perc-symbol');
                pSymElem.innerText = '%';
                formCol.appendChild(pSymElem);
            }

            formRow.appendChild(formCol);
        });

        formContainer.appendChild(formRow);
    });
}

fileContainer.addEventListener('dragover', e => {
    e.preventDefault();

    fileContainer.style.border = 'solid 1px #C0B283';
}, false);

fileContainer.addEventListener('drop', e => {
    e.preventDefault();
    e.stopPropagation();

    let files = [...e.dataTransfer.files];

    const packageFile = files.find(f => /\.apf/);
    if (packageFile) {
        const returnValue = requestAttemptUpdate(packageFile);

        if (returnValue) {
            showPrompt('Update successful.', 1000);
        }
    }

    files = files
        .map(f => f.path)
        .filter(f => /\.(xls|xlsx)$/.test(f));

    let fileList;

    if (inputFiles.length < 1) {
        clearNode(fileContainer);

        fileContainer.classList.add('file-input-occupied');
        fileList = document.createElement('UL');
        fileList.setAttribute('id', 'file-list');

        fileContainer.appendChild(fileList);
    } else {
        fileList = document.querySelector('#file-list');
    }

    files.forEach(file => {
        if (inputFiles.indexOf(file) !== -1) {
            return;
        }

        inputFiles.push(file);

        const fileNode = document.createElement('LI');
        fileNode.classList.add('file-node');
        fileNode.setAttribute('file-path', file);
        fileNode.innerText = file.match(/\/([A-Za-z0-9_-]|\s|\.)+$/)[0].slice(1);

        const deleteNodeButton = document.createElement('BUTTON');
        deleteNodeButton.classList.add('delete-node-button');
        deleteNodeButton.innerText = 'close';

        deleteNodeButton.addEventListener('click', e => {
            const target = e.currentTarget;
            const filePath = target.parentNode.getAttribute('file-path');

            inputFiles.splice(inputFiles.indexOf(filePath), 1);
            target.parentNode.remove();

            if (inputFiles.length < 1) {
                fileContainer.classList.remove('file-input-occupied');
                fileContainer.innerText = 'Saldo';
            }
        }, false);

        fileNode.appendChild(deleteNodeButton);
        fileList.appendChild(fileNode);
    });

    fileContainer.style.border = '';
}, false);

fileContainer.addEventListener('dragleave', e => {
    e.preventDefault();

    fileContainer.style.border = '';
}, false);

const finalRegEx = {
    int: /^\d+$/,
    float: /^((\d+\.\d*)|(\.?\d+))$/,
    percentage: /^((\d+\.\d*)|(\.?\d+))$/
};

build.addEventListener('click', catalyzeBuild, false);

renderForm(currentForm);
