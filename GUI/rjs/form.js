const formContainer = document.querySelector('#form-container');
const fileContainer = document.querySelector('#file-container');

const messagePrompt = document.querySelector('#message-prompt');

const buildButton = document.querySelector('#build');

let addButton;

const form = {
    form: [
        [
            {
                id: 'indexador',
                label: 'Indexador',
                type: 'float',
                width: 25
            },
            {
                id: 'pu-emis',
                label: 'P.U. de Emissão',
                type: 'float',
                width: 25
            },
            {
                id: 'total',
                label: 'Total',
                type: 'float',
                width: 25
            },
            {
                id: 'starting-date',
                label: 'Data',
                type: 'string',
                width: 25
            }
        ],
        [
            {
                id: 'r-sub',
                label: 'R. Subordinado',
                type: 'percentage',
                group: 'razoes',
                width: 25
            },
            {
                id: 'r-sen',
                label: 'R. Sênior',
                type: 'percentage',
                group: 'razoes',
                width: 25
            },
            {
                id: 'target-irr',
                label: 'TIR Projetado',
                type: 'percentage',
                width: 25
            },
            {
                id: 't-em-senior-anual',
                label: 'T.A. Emissão Sênior',
                type: 'percentage',
                group: 'taxas-juros',
                width: 25
            }
        ],
        [
            {
                id: 'c-period',
                label: 'P. Carência',
                type: 'int',
                width: 25
            },
            {
                id: 'fr-previsto',
                label: 'F.R. Previsto',
                type: 'float',
                width: 25
            },
            {
                id: 'pmt-proper',
                label: 'PMT Projetado',
                type: 'percentage',
                width: 25
            },
            {
                id: 'despesas',
                label: 'Despesas',
                type: 'float',
                width: 25
            }
        ],
        [
            {
                id: 'mezanino',
                label: 'Mezanino',
                type: 'list',
                width: 100,
                inputs: [
                    {
                        label: 'Razão',
                        type: 'percentage',
                        group: 'razoes',
                        width: 50
                    },
                    {
                        label: 'T.A. Emissão',
                        type: 'percentage',
                        width: 50
                    }
                ],
                max: 1
            }
        ]
    ]
}

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

const finalRegEx = {
    int: /^\d+$/,
    float: /^((\d+\.\d*)|(\.?\d+))$/,
    percentage: /^((\d+\.\d*)|(\.?\d+))$/,
    string: /^(Jan|Fev|Mar|Abr|Mai|Jun|Jul|Ago|Set|Out|Nov|Dez)\/\d{4}$/
};

function catalyzeBuild() {
    let values = [];

    formContainer.childNodes.forEach(row => {
        row.childNodes.forEach(col => {
            if (col.classList.contains('form-col-list')) return;

            const input = col.childNodes[1];
            values.push([
                input.value,
                input.getAttribute('data-type'),
                col.childNodes[0].innerText,
                input.id,
                input.getAttribute('data-group')
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
                if (value[4] !== 'undefined') {
                    if (inputs.hasOwnProperty(value[4])) {
                        inputs[value[4]].push(value[0])
                    } else {
                        inputs[value[4]] = [value[0]];
                    }
                } else {
                    inputs[value[3]] = value[0];
                }
            });
            inputs.inputFiles = inputFiles;
            inputs.outputFile = requestSaveDialog();

            if (inputs.outputFile) {
                let mezanineLayers = addButton ? [JSON.parse(addButton.getAttribute('data-value'))] : [];
                mezanineLayers.forEach(layer => {
                    inputs['razoes'].splice(inputs['razoes'].length - 1, 0, layer[0]);
                    inputs['taxas-juros'].splice(inputs['taxas-juros'].length - 1, 0, layer[1]);
                });

                requestRunScript(inputs);
            }
        }
    }
}

function createInput(type, group, id, label, formCol, isList = false) {
    const input = document.createElement('INPUT');

    input.setAttribute('data-type', type);
    input.setAttribute('data-group', group);
    input.setAttribute('id', id);
    input.setAttribute('type', 'text');

    if (type === 'percentage') {
        input.classList.add('percentage-input');
    } else {
        input.classList.add('standard-input');
    }

    const inputLabel = document.createElement('LABEL');
    inputLabel.classList.add(isList ? 'text-input-label-list' : 'text-input-label')
    inputLabel.setAttribute('for', id);
    inputLabel.innerText = label;

    formCol.appendChild(inputLabel);

    input.addEventListener('keydown', e => {
        const t = e.currentTarget;
        const type = t.getAttribute('data-type');

        const labelElem = t.parentNode.firstChild;
        const pSymElem = t.parentNode.childNodes[2];

        if (e.key === 'Enter') {
            catalyzeBuild();
        } else if (e.key.length < 2) {
            e.preventDefault();

            const value = t.value + e.key;
            if (
                type === 'string' && /^[A-Za-z0-9/]+$/.test(value) ||
                type === 'int' && /^\d+$/.test(value) ||
                (type === 'percentage' || type === 'float') && /^((\d*\.\d+)|(\d+\.?))$/.test(value)
            ) {
                const cursorPos = t.selectionStart;
                let nValue = t.value.split('');
                nValue.splice(cursorPos, 0, e.key);
                t.value = nValue.join('');
                t.setSelectionRange(cursorPos + 1, cursorPos + 1);
            }
        }

        const vLength = t.value.length;
        if (t.value && !(e.key === 'Backspace' && t.selectionStart === vLength && vLength < 2)) {
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

    return input;
}

// When extending cap, remember to update value at the button
let mezanineLayersCount = 0;
let dblWindow;

function renderForm(form) {
    clearNode(formContainer);

    form.form.forEach(row => {
        const formRow = document.createElement('DIV');
        formRow.classList.add('form-row');

        row.forEach(col => {
            const formCol = document.createElement('DIV');

            const { id, label, type, group, width } = col;

            formCol.style.width = `${width}%`;

            if (
                type === 'percentage' ||
                type === 'float' ||
                type === 'int' ||
                type === 'string'
            ) {
                formCol.classList.add('form-col');

                const inputElem = createInput(type, group, id, label, formCol);
                formCol.appendChild(inputElem);

                if (type === 'percentage') {
                    const pSymElem = document.createElement('LABEL');
                    pSymElem.classList.add('perc-symbol');
                    pSymElem.innerText = '%';
                    formCol.appendChild(pSymElem);
                }
            } else if (type === 'list') {
                formCol.classList.add('form-col-list');

                const listWrapper = document.createElement('DIV');
                listWrapper.classList.add('list-wrapper');

                addButton = document.createElement('BUTTON');
                addButton.classList.add('add-button');
                addButton.setAttribute('id', id);
                addButton.setAttribute('data-type', 'list');
                addButton.setAttribute('data-value', '[]');
                addButton.innerText = '+';

                listWrapper.appendChild(addButton);

                addButton.addEventListener('click', () => {
                    if (mezanineLayersCount < col.max) {
                        const inputRow = document.createElement('DIV');
                        inputRow.classList.add('input-row');

                        inputRow.addEventListener('contextmenu', e => {
                            dblWindow = e.currentTarget;
                            setTimeout(() => { dblWindow = undefined }, 3000);
                        }, false);

                        inputRow.addEventListener('click', e => {
                            if (dblWindow === e.currentTarget) {
                                e.currentTarget.remove();
                                addButton.setAttribute('data-value', '[]');
                                mezanineLayersCount--;
                            }
                        });

                        col.inputs.forEach((input, i) => {
                            const inputRowCol = document.createElement('DIV');
                            inputRowCol.classList.add('input-row-col');
                            inputRowCol.style.width = `${input.width}%`;

                            const inputElem = createInput(input.type, input.group, i, input.label, inputRowCol, true);
                            inputRowCol.appendChild(inputElem);

                            if (input.type === 'percentage') {
                                const pSymElem = document.createElement('LABEL');
                                pSymElem.classList.add('perc-symbol');
                                pSymElem.innerText = '%';
                                inputRowCol.appendChild(pSymElem);
                            }

                            inputElem.addEventListener('keydown', e => {
                                const targetInput = e.currentTarget;
                                let currentValue = JSON.parse(addButton.getAttribute('data-value'));

                                currentValue[targetInput.id] = targetInput.value;

                                addButton.setAttribute('data-value', JSON.stringify(currentValue));
                            }, false);

                            inputRow.appendChild(inputRowCol);
                        });

                        listWrapper.appendChild(inputRow);
                        mezanineLayersCount++;
                    }
                }, false);

                formCol.appendChild(listWrapper);
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

    const packageFile = files.find(f => /\.apf$/.test(f.path));
    if (packageFile) {
        const returnValue = requestAttemptUpdate(packageFile.path);

        if (returnValue === 0) {
            showPrompt('Update successful.', 2000);
        }
    }

    files = files
        .map(f => f.path)
        .filter(f => /\.(xls|xlsx)$/.test(f));

    let fileList;

    if (inputFiles.length < 1 && files.length) {
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

buildButton.addEventListener('click', catalyzeBuild, false);

renderForm(form);
