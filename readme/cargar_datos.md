## Cargar Datos estaticos a la Base de Datos

Ingresar al shell, dentro del entorno virtual
~~~
python manage.py shell
~~~
### Agregar lista de permisos
Agregar la siguiente linea
~~~
from oauth_project.models.modelos import Permiso
~~~
Añadir los registros
~~~
er = Permiso.objects.create(descripcion = "Ver Usuarios")
per = Permiso.objects.create(descripcion = "Activar USuarios")
per = Permiso.objects.create(descripcion = "Desactivar Usuarios")
per = Permiso.objects.create(descripcion = "Ver Permisos")
per = Permiso.objects.create(descripcion = "Ver Roles")
per = Permiso.objects.create(descripcion = "Crear Roles")
per = Permiso.objects.create(descripcion = "Modificar Roles")
per = Permiso.objects.create(descripcion = "Eliminar Roles")
per = Permiso.objects.create(descripcion = "Asignar Roles")
per = Permiso.objects.create(descripcion = "Ver Proyectos")
per = Permiso.objects.create(descripcion = "Crear Proyectos")
per = Permiso.objects.create(descripcion = "Modificar Proyectos")
per = Permiso.objects.create(descripcion = "Cancelar Proyectos")
per = Permiso.objects.create(descripcion = "Ver Tablero Kanban")
per = Permiso.objects.create(descripcion = "Iniciar Proyecto")
per = Permiso.objects.create(descripcion = "Cancelar Proyecto")
per = Permiso.objects.create(descripcion = "Finalizar Proyecto")
per = Permiso.objects.create(descripcion = "Crear Sprint")
per = Permiso.objects.create(descripcion = "Crear US")
per = Permiso.objects.create(descripcion = "Cancelar Sprint")
per = Permiso.objects.create(descripcion = "Ver Product Backlog")
~~~
Para guardar los cambios en la Base de datos
~~~
per.save()
~~~
Luego verificar la tabla oauth_project_permiso en la base de datos

### Agregar lista de Estados del Proyecto

