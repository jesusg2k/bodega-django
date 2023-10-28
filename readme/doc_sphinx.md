# Generación de documentacion con Sphinx

### Pre-condiciones
Primero debe ingresar al entorno virtual para su proyecto Django
~~~
source virtual-env/bin/activate
~~~
#### Instalar Sphinx
~~~
pip install sphinx
~~~
### Crear un directorio de documentación
Se debe crear un directorio en la carpeta raiz que contendrá la documentacion del proyecto
~~~
mkdir docs
~~~
En la carpeta docs ejecutar el siguiente comando para iniciar Sphinx
~~~
cd docs
sphinx-quickstart
~~~
Saldran varias opciones de creacion
~~~
Bienvenido a la utilidad de inicio rápido de Sphinx 5.1.1.

Ingrese los valores para las siguientes configuraciones (solo presione Entrar para
aceptar un valor predeterminado, si se da uno entre paréntesis).

Ruta raíz seleccionada: .

Tiene dos opciones para colocar el directorio de compilación para la salida de Sphinx.
O usas un directorio "_build" dentro de la ruta raíz, o separas
directorios "fuente" y "compilación" dentro de la ruta raíz.
> Separar directorios fuente y compilado (y/n) [n]: y

El nombre del proyecto aparecerá en varios lugares en la documentación construida.
> Nombre de proyecto: systemmanager
> Autor(es): autor/es
> Liberación del proyecto []: 1.0

Si los documentos deben escribirse en un idioma que no sea inglés,
puede seleccionar un idioma aquí por su código de idioma. Sphinx entonces
traducir el texto que genera a ese idioma.

Para obtener una lista de códigos compatibles, vea
https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-language.
> Lenguaje del proyecto [en]: es
~~~
Para compilar los documentos
~~~
make builder
~~~
## Conexion con Django
El la carpeta del proyecto ir a **docs/source/conf.py** y agregar en la parte superior del archivo las siguientes lineas
~~~
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))
~~~
Para activar las extensiones buscamos en el archivo de configuración conf.py, en la sección de extensiones y colocamos
~~~
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary', 
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode'
]
~~~

**sphinx-apidoc** para generar documentación completamente automática
Navegar al directorio /docs y ejecutar
~~~
sphinx-apidoc -o . ..
~~~
Para generar la documentacion de los modulos
~~~
sphinx-apidoc -o source/api ..
~~~
Por último, se necesita construir la documentación
~~~
make html
~~~
Para visualizar la documentaciòn, abrir el archivo que se encuentra en el siguiente path
~~~
project_name/docs/build/html/index.html
~~~