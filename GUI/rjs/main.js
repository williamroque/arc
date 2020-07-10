const remote = require('electron').remote;

const formContainer = document.querySelector('#form-container');

let formSchemata = Communication.requestFormSchemata();

let forms = [];
let currentForm;

for (const schema of formSchemata) {
    const form = new Form(schema, formContainer);
    if (schema.isDefault) {
        currentForm = form;
    }

    forms.push(form);
}

if (currentForm) {
    currentForm.activate();
}

Communication.addListener('update-form', (_, formID) => {
    currentForm = forms.find(form => form.schema.packageName === formID);
    currentForm.activate();
});

document.querySelector('#close').addEventListener('click', () => {
    remote.getCurrentWindow().close();
}, false);

document.querySelector('#build').addEventListener('click', () => {
    const values = currentForm.valuesContainer;
    if (values.areAllValid()) {
        Communication.requestRunScript(
            values.parse(),
            currentForm.schema
        );
    }
});