    var prev_handler = window.onload;
    window.onload = function () {
        console.log("")
        if (prev_handler) {
            prev_handler();
        }


        console.log("se arreglan traducciones y problemas del propio framework")
        //arreglar traducciones via javascript

        //se traduce el type to search de los select
        var inputs = document.getElementsByClassName("choices__input choices__input--cloned");
        console.log((inputs.length))
        for (let i = 0; i < inputs.length; i++) {
            inputs[i].placeholder = 'Escriba para realizar una búsqueda'
        }

        console.log(document.getElementById('tabla-potenciada_filter'))

        //se traduce el add another del boton de los datagrip
        var inputs = document.getElementsByClassName("formio-button-add-row");
        console.log((inputs.length))
        console.log(inputs)

        for (let i = 0; i < inputs.length; i++) {
            console.log("se va cambiar")
            console.log((inputs[i]))
            //console.log((inputs[i].textContent))
            inputs[i].innerHTML = inputs[i].innerHTML = "Agregar otro"
            inputs[i].textContent = inputs[i].textContent("Add Another", "Agregar otro")
        }





    };

