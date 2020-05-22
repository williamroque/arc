const remote = require('electron').remote;

const formContainer = document.querySelector('#form-container');

let formSchemata = Communication.requestFormSchemata();

let forms = [];
let currentForm;
function constructForms() {
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
}

Communication.addListener('update-form-schemata', (_, updatedSchemata) => {
    formSchemata = updatedSchemata;
    constructForms();
});

constructForms();

document.querySelector('#close').addEventListener('click', () => {
    remote.getCurrentWindow().close();
}, false);
