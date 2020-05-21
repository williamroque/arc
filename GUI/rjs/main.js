const remote = require('electron').remote;

const formContainer = document.querySelector('#form-container');

const formSchemata = Communication.requestFormSchemata();

let currentForm;

let forms = [];
formSchemata.forEach(schema => {
    const form = new Form(schema, formContainer);
    if (schema.isDefault) {
        currentForm = form;
    }

    forms.push(form);
});

if (currentForm) {
    currentForm.render();
}

document.querySelector('#close').addEventListener('click', () => {
    remote.getCurrentWindow().close();
}, false);
