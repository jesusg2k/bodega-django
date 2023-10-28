datagrid = data.dataGrid
var n = datagrid.length
console.log('n -> '+n)
objects = {};
valido = true
msg = ""

do_exist = false
doing_exist = false
done_exist = false


for(let i=0; i<n; i++){
  console.log("i: "+i+"/"+n)
  for(const key in datagrid[i]){
    if(valido===false) {
        console.log('se detiene el for -> break por invalido')
        break;
    }
    console.log("key: "+key+" of [i]-> "+i)
    console.log('datagrid[i][key]->'+datagrid[i][key])
    if(datagrid[i][key]===""){
        valido = false
        msg = 'Error: Hay un elemento vacio'
        console.log('inválido, hay un elemento vacío')
        break;
    }
    if(!key.includes('unique')){ continue; }
        if((objects[datagrid[i][key]]) != undefined){
          console.log('este se repite->'+datagrid[i][key])
          valido = false
          msg = "Hay elementos repetidos"
          console.log('se detiene porque se repiten valores')
          break;
        }
    console.log('se asigna valor a datagrid['+i+']['+key+']->'+1)
  	objects[datagrid[i][key]] = 1
    if(datagrid[i][key]==="done") {done_exist=true}
    if(datagrid[i][key]==="do") {do_exist=true}
    if(datagrid[i][key]==="doing") {doing_exist=true}
    }
}

if(!do_exist || !doing_exist || !done_exist) {
        valido = false
        msg = 'Los campos do, doing y done son obligatorios'
}

if(valido===true){
    valid = true;
}else{
    valid = msg
}



