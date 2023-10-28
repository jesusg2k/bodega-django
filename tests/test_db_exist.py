import pytest
from django.contrib.auth.models import User

from oauth_project import settings
from oauth_project.models.modelos import Estado, Proyecto, Equipo, Permiso, Integrante, Miembro, RolProyecto, Sprint, \
    TipoUserStory, UserStory

pytestmark = [pytest.mark.django_db(databases=["tests_db"])]

@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['test'] = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'systemtest',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }



@pytest.mark.django_db
def test_exist_sprint():
    """
            Metodo test_exist_sprint::

                    def test_exist_sprint():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad Sprint

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

    """
    estados = Estado.objects.all().count()
    assert estados == 4


@pytest.mark.django_db
def test_permisos_lista():

    """
            Metodo test_permisos_lista::

                    def test_permisos_lista():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad Permisos

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

    """
    permisos = Permiso.objects.all()
    assert permisos.count() >= 29


@pytest.mark.django_db
def test_permisos_exacto():
    """
            Metodo test_permisos_exacto::

                    def test_permisos_exacto():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad test_permisos_exacto

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

    """
    assert Permiso.objects.all().count() == 29

@pytest.mark.django_db
def test_exist_user():
    """
            Metodo test_exist_user::

                    def test_exist_user():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad User

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

    """
    assert User.objects.first() is not None

@pytest.mark.django_db
def test_exist_proyecto():
    """
            Metodo test_exist_proyecto::

                    test_exist_proyecto():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad Proyecto

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

    """
    assert Proyecto.objects.first() is not None

@pytest.mark.django_db
def test_exist_equipo():
    """
            Metodo test_exist_equipo::

                    test_exist_equipo():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad Equipo

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

    """
    assert Equipo.objects.first() is not None

@pytest.mark.django_db
def test_exist_us():
    """
            Metodo test_exist_us::

                    def test_exist_us():

            Metodo y comprobar si la existencia mínima de la entidad UserStory

            Consigue una sesion a través de la configuración de la BD en settings ['test']
            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.

            Args:

            Returns:

    """
    assert UserStory.objects.first() is not None

@pytest.mark.django_db
def test_cantidad_minimo_user_story():
    """
            Metodo test_cantidad_minimo_user_story::

                    def test_cantidad_minimo_user_story():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad US

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

    """
    assert UserStory.objects.all().count() > 10




@pytest.mark.django_db
def test_cantidad_minimo_miembros():
    """
            Metodo test_cantidad_minimo_miembros::

                    def test_cantidad_minimo_miembros():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad Miembros

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

            """
    assert Miembro.objects.all().count() > 4


@pytest.mark.django_db
def test_cantidad_minimo_rol_proyecto():
    """
            Metodo test_cantidad_minimo_rol_proyecto::

                    def test_cantidad_minimo_rol_proyecto():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad RolProyecto

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

            """
    assert RolProyecto.objects.all().count() >= 6

@pytest.mark.django_db
def test_cantidad_minimo_tipo_us():
    """
            Metodo test_cantidad_minimo_tipo_us::

                    def test_cantidad_minimo_tipo_us():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad Tipo US

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

            """
    assert TipoUserStory.objects.all().count() >= 3

@pytest.mark.django_db
def test_cantidad_minimo_integrantes():
    """
            Metodo test_cantidad_minimo_integrantes::

                    def test_cantidad_minimo_integrantes():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad Integrantes

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

            """
    assert Integrante.objects.all().count() >= 3

@pytest.mark.django_db
def test_minimo_sprint_lista():
    """
            Metodo test_minimo_sprint_lista::

                    def test_minimo_sprint_lista():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad Sprint

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

            """
    sprints = Sprint.objects.all()
    assert sprints.count() >= 3

@pytest.mark.django_db
def test_cant_minima_users():
    """
            Metodo test_cant_minima_users::

                    def test_cant_minima_users():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad Users

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

            """
    assert User.objects.all().count() > 5

@pytest.mark.django_db
def test_cantidad_minimo_proyectos():
    """
            Metodo test_cantidad_minimo_proyectos::

                    def test_cantidad_minimo_proyectos():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad Proyecto

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

            """
    assert Proyecto.objects.all().count() >= 2

@pytest.mark.django_db
def test_cantidad_minimo_equipo():
    """
            Metodo test_cantidad_minimo_equipo::

                    def test_cantidad_minimo_equipo():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad Equipo

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

            """
    assert Equipo.objects.all().count() >= 2

@pytest.mark.django_db
def test_cantidad_minimo_miembros():
    """
            Metodo test_cantidad_minimo_miembros::

                    def test_cantidad_minimo_miembros():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad Miembros

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

            """
    assert Miembro.objects.all().count() > 4

@pytest.mark.django_db
def test_cantidad_minimo_rol_proyecto():
    """
            Metodo test_cantidad_minimo_rol_proyecto::

                    def test_cantidad_minimo_rol_proyecto():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad RolProyecto

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

            """
    assert RolProyecto.objects.all().count() >= 6

@pytest.mark.django_db
def test_cantidad_minimo_tipo_us():
    """
            Metodo test_cantidad_minimo_tipo_us::

                    def test_cantidad_minimo_tipo_us():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad Tipo US

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

            """
    assert TipoUserStory.objects.all().count() >= 3

@pytest.mark.django_db
def test_cantidad_minimo_integrantes():
    """
            Metodo test_cantidad_minimo_integrantes::

                    def test_cantidad_minimo_integrantes():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad Integrante

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

            """
    assert Integrante.objects.all().count() >= 3

@pytest.mark.django_db
def test_minimo_sprint_lista():
    """
            Metodo test_minimo_sprint_lista::

                    def test_minimo_sprint_lista():

            Metodo para facilitar y comprobar si la existencia mínima de la entidad Sprint

            Obtiene la session de la BD con la cual realiza las querys respectivas y luego realiza un assert de existencia.


            Args:

            Returns:

            """
    sprints = Sprint.objects.all()
    assert sprints.count() >= 3
