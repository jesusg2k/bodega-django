# **Preparación de Entornos Django**

*Preparando el entorno de desarrollo y producción*
## Requerimientos
* Ubuntu 20.04
* Python 3.10
* Postgres 13
* Nginx 1.18
* Django

## Instalación
Procedemos a instalar de forma general los requerimientos

~~~
sudo apt update
sudo apt install python-pip python-dev libpq-dev postgresql postgresql-contrib nginx curl
~~~

**Proyecto** Podemos clonar el proyecto de nuestro repositorio de gitlab, siempre en la carpeta
~~~
cd /home/<user/
mkdir proyecto
cd proyecto
git clone https://gitlab.com/FNVG/is2-grupo20-system-manager.git
~~~

**Entorno Virtual** Preparamos el entorno virtual, creando uno nuevo, e instalando todos los requerimientos del proyecto ubicados
en el archivo requirements.txt
~~~
python3 -m virtual virtual-env
source virtual-env/bin/activate
pip install -r /home/<user>/proyecto/requirements.txt
~~~
En caso de error al crear el entorno virtual
~~~
python -m venv ./virtual-env
~~~

**Base de datos** También debemos contar con una base de datos Postgres. Creamos una base de datos llamada systemmanager,
cambiamos la contraseña del usuario 'postgres' y creamos un usuario nuevo
~~~
sudo -u postgres psql
CREATE DATABASE systemmanagerdb
ALTER USER postgres WITH PASSWORD 'postgres';
CREATE USER usuariosystem WITH PASSWORD 'password'
GRANT ALL PRIVILEGES ON DATABASE systemmanagerdb TO proyecto;
~~~

**Ejecucción de migraciones:** Ejecutamos las migraciones en caso de que nuestra base de datos no este actualizada o sea nueva
~~~
python manage.py makemigrations
python manage.py migrate
~~~
**Creación de superusuario Django:** Este es el usuario con permisos totales que puede modificar el comportamiento y
configuración de nuestra aplicación django
~~~
python manage.py createsuperuser
~~~
### ¡Felicidades si has llegado hasta este paso!
Con esto debería estar preparado el entorno de desarrollo Verificamos ejecutando el runserver En caso de tener problemas,
podemos permitir al firewall el puerto 8000
~~~
python manage.py runserver
sudo ufw allow 8000 (en caso de problemas)
~~~
## Entorno de Producción
**Vamos a ejecutar manualmente Unicorn:** Este es un servidor HTTP para Python que soporta WSGI, Django y Paster de forma
nativa
~~~
cd /home/<usuario>/proyecto
gunicorn --bind 127.0.0.1:8000 <proyect_name>.wsgi
gunicorn --bind 127.0.0.1:8000 oauth_project.wsgi
(en nuestro caso se llama, oauth_project)
~~~
**Contenido estático:** Recolectamos todo el contenido estático en la ubicación del directorio que configuramos
~~~
Estando en la carpeta del proyecto, podemos recolectar todo el contenido estatico
cd /myprojectdir/manage.py collectstatic
~~~
**Creación de archivos de socket y configuración de servicio systemd para Gunicorn** Antes que nada salimos del entorno virtual de
Python Creamos el archivo de socket de systemd
~~~
sudo nano /etc/systemd/system/gunicorn.socket
~~~
Dentro del cual guardaremos lo siguiente:
~~~
[Unit]
Description=gunicorn socket
[Socket]
ListenStream=/run/gunicorn.sock
[Install]
WantedBy=sockets.target
~~~
Guardamos y cerramos el archivo

**Creación archivo de servicio systemd para Gunicorn** En este archivo especificamos el usuario que va ejecutar el proceso, el
directorio del proyecto y el comando a ser ejecutado con sus respectivos parametros de Gunicorn.
~~~
sudo nano /etc/systemd/system/gunicorn.service
~~~
~~~
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target
[Service]
User=<user>
Group=www-data
WorkingDirectory=/home/<user>/proyecto
ExecStart=/home/<user>/proyecto/virtual-env/bin/gunicorn \
--access-logfile - \
--workers 3 \
--bind unix:/run/gunicorn.sock \
oauth_project.wsgi:application
[Install]
WantedBy=multi-user.target
~~~
**Guardamos y cerramos el archivo Obs:** en caso de realizar cambios en el futuro para recargar el archivo podemos ejecutar los
siguientes comandos
~~~
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
~~~
**Inicio del Gunicorn e inicio automático** Ahora podemos iniciar y habilitar el socket de Gunicorn. También se creará
automáticamente el archivo de socket /run/gunicorn.sock
~~~
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
~~~
Podemos comprobar la existencia del archivo gunicorn.sock en el directorio /run :
~~~
file /run/gunicorn.sock
~~~
Podemos verificar que el Gunicorn se active de forma automática, podemos consultar el estado de gunicorn y enviar una
petición al localhost para activar manualmente el unicorn
~~~
sudo systemctl status gunicorn
curl --unix-socket /run/gunicorn.sock localhost
sudo systemctl status gunicorn
~~~
**NGINX** Configuramos NGINX para transferir el tráfico al proceso de Gunicorn. Creamos un archivo y abrimos un nuevo bloque de
servidor en la carpeta sites-available de Nginx
~~~
sudo nano /etc/nginx/sites-available/proyecto
~~~
En el cual se debe escribir lo siguiente
~~~
server {
    listen 90;
    server_name localhost;
    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/jesus/proyecto;
    }
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
~~~
Guarde y cierre el archivo cuando termine. Ahora, podemos habilitar el archivo vinculándolo al directorio sites-enabled
Guardamos el archivo y lo cerramos, luego procedemos a habilitar el archivo vinculándolo al directorio sites-enabled.
~~~
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
~~~
Para comprobar que la configuración de NGINX sea correcta podemos ejecutar:
~~~
sudo nginx -t
~~~
En caso de no notificar errores, podemos reiniciar el servidor:
~~~
sudo systemctl restart nginx
~~~
Por último damos permiso a los puertos de Nginx y sacamos los permisos al puerto 8000 disponibles:
~~~
sudo ufw delete allow 8000
sudo ufw allow 'Nginx Full'
~~~
### ¡Felicidades si has llegado hasta este paso!
**Con esto debería estar preparado el entorno de producción con Nginx funcionando**