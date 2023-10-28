import pytest
from allauth.account.utils import filter_users_by_username
from django.contrib.auth.models import User


from oauth_project.models.modelos import Estado, Proyecto, Equipo, Permiso, Integrante, Miembro, RolProyecto

"""
                Metodo test_debe_crear_usuario_con_nombre::

                        def test_debe_crear_usuario_con_nombre(db):

                Metodo para comprobar si se puede crear un usuario exitosamente

                Intenta crear un usuario

                Genera que el test falle en caso de no poder, y es un caso exitoso en el caso de que se realice correctamente

                Args:
                    
                Returns:
                        
                """
@pytest.mark.django_db
def test_debe_crear_usuario_con_nombre(db) -> None:
    user = User.objects.create_user("Haki")
    assert user.username == "Haki"

@pytest.mark.django_db
def test_debe_chequear_password(db) -> None:
    user = User.objects.create_user("usuarioA")
    user.set_password("password")
    assert user.check_password("password") is True

@pytest.fixture
def crear_user(db) -> User:
    return User.objects.create_user(username="usuarioTesting", email="usuarioTesting2@gmail.com", password="libros01")

def test_user_existe(crear_user):
    assert User.objects.filter(username="usuarioTesting").exists()

@pytest.fixture(params=("DO", "DONE", "DOING"))
def crear_estado(db,request) -> Estado:
    return Estado.objects.create(descripcion=request.param)


def test_filter_estado(crear_estado):
    assert Estado.objects.filter(descripcion="DO").exists() or Estado.objects.filter(descripcion="DOING").exists() or Estado.objects.filter(descripcion="DONE").exists()



@pytest.fixture
def crear_proyecto(crear_user, crear_estado) -> Proyecto:
    return Proyecto.objects.create(nombre_proyecto="ProyectoA",
                                   descripcion="descripcionA",
                                   scrum_master=crear_user,
                                   creado_by=crear_user.id,
                                   estado= crear_estado
                                   )

def test_proyecto_filter(crear_proyecto):
    assert Proyecto.objects.filter(nombre_proyecto="ProyectoA").exists()

@pytest.fixture
def crear_permiso(db) -> Permiso:
    return Permiso.objects.create(descripcion="permiso1")

def test_permiso_filter(crear_permiso):
    assert Permiso.objects.filter(descripcion="permiso1").exists()

@pytest.fixture
def crear_equipo(crear_proyecto) -> Equipo:
    return Equipo.objects.create(proyecto=crear_proyecto,
                                 capacidad=2
                                 )


def test_crear_equipo(crear_equipo):
    assert Equipo.objects.filter(capacidad=2).exists()





@pytest.fixture
def crear_integrante(crear_equipo, crear_user) -> Integrante:
    return Integrante.objects.create(
        integrante=crear_user,
        equipo=crear_equipo,
        cant_horas_dias=4
    )


def test_crear_integrante(crear_integrante):
    assert Integrante.objects.filter(cant_horas_dias=4).exists()




@pytest.fixture
def crear_user(db) -> User:
    return User.objects.create_user(username="usuarioTesting", email="usuarioTesting2@gmail.com", password="libros01")


def test_verificar_estados_cargados(crear_estado) -> Estado:
    assert Estado.objects.all().count() == 1

