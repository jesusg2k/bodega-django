Formio.icons = 'fontawesome';
    Formio.createForm(document.getElementById('formio'), {
    components: [
        { type: 'select', label: 'Model',
            key: 'model', placeholder: 'Select your model',
            dataSrc: 'url', defaultValue: 'Pilot',
            lazyLoad: false, data: { url: 'https://vpic.nhtsa.dot.gov/api/vehicles/getmodelsformake/honda?format=json' },
            valueProperty: 'Model_Name',
            template: 'hola'
        },
        {
            "type": "button",
            "label": "Submit",
            "key": "submit",
            "disableOnInvalid": true,
            "input": true,
            "tableView": false
        }
  ]
}).then(function(form) {
  form.on('submit', function(submission) {

  });
});
