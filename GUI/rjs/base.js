const formContainer = document.querySelector('#form-container');
const fileContainer = document.querySelector('#file-container');

const messagePrompt = document.querySelector('#message-prompt');

const buildButton = document.querySelector('#build');

let mezanineLayers = [];


let inputFiles = [];

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
    const firstInvalid = values.find(v => !finalRegEx[v[1]].test(v[0]));

    if (firstInvalid) {
        showPrompt(`Valor inválido no campo <b>${firstInvalid[2].toLowerCase()}</b>.`, 2000);
    } else if (mezanineLayers.some(layer => layer.some(v => !v || !finalRegEx.float.test(v)))) {
        showPrompt('Valor inválido no campo <b>Mezanino</b>.', 2000);
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
                mezanineLayers.forEach(layer => {
                    inputs['razoes'].splice(inputs['razoes'].length - 1, 0, layer[0].replace(/\./g, '').replace(/,/g, '.'));
                    inputs['taxas-juros'].splice(inputs['taxas-juros'].length - 1, 0, layer[1].replace(/\./g, '').replace(/,/g, '.'));
                });

                requestRunScript(inputs);
            }
        } else {
            showPrompt('Campo <b>Saldos</b> indefinido.', 2000);
        }
    }
}

                addButton.addEventListener('click', () => {
                    if (mezanineLayers.length < col.max) {
                        const inputRow = document.createElement('DIV');
                        inputRow.classList.add('input-row');
                        inputRow.setAttribute('data-index', mezanineLayers.length);
                        mezanineLayers.push([null, null]);


                            if (input.type === 'percentage') {
                                const pSymElem = document.createElement('LABEL');
                                pSymElem.classList.add('perc-symbol');
                                pSymElem.innerText = '%';
                                inputRowCol.appendChild(pSymElem);
                            }

                            inputElem.addEventListener('keyup', e => {
                                const target = e.currentTarget;
                                const rowIndex = target.parentNode.getAttribute('data-index') | 0;
                                const colIndex = target.getAttribute('id') | 0;


buildButton.addEventListener('click', catalyzeBuild, false);

renderForm(form);
