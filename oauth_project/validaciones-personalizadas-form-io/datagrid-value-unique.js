/*Valida que no hay elementos con keys que incluyen 'unique' repetidos, y al mismo tiempo que no sean vacios.*/
console.log(data.dataGrid.length)
console.log(data.dataGrid)
var n = data.dataGrid.length
objects = {};
datagrid = data.dataGrid
valido = true
console.log(valido)
for(let i=0; i<n; i++){
  for(const key in datagrid[i]){
    console.log('nombre key-> '+key)
    if(datagrid[i][key].isEmpty()){
        valid = 'Error: Hay un elemento vacio';
        break;
    }
    if(!key.includes('unique')){ continue; }
  	if((objects[datagrid[i][key]]) != undefined){
      console.log('este se repite->'+datagrid[i][key])
      valido = false
  	}
  	objects[datagrid[i][key]] = 1
    }
}
if(!valid.includes('Error')){
    valid = (valido)? true : "Hay valores repetidos"
}

