from django.urls import include, path

from rest_framework import routers

from oauth_project.serializers import MiembroSerializer
from oauth_project.views import PermisoViewSet, UsuarioViewSet, ProyectoViewSet, RolProyectoViewSet, \
   MiembroProyectoViewSet, TipoUserStoryViewSet, EstadoViewSet, TipoVentaViewSet, ClienteViewSet, ProductoActivosViewSet

router = routers.DefaultRouter()
router.register(r'permisos', PermisoViewSet)
router.register(r'users', UsuarioViewSet)
router.register(r'proyectos', ProyectoViewSet)
router.register(r'roles', RolProyectoViewSet)
router.register(r'miembros-proyectos', MiembroProyectoViewSet)
router.register(r'tipos-users-story', TipoUserStoryViewSet)
router.register(r'estados', EstadoViewSet)
router.register(r'tipo_venta', TipoVentaViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'productos-activos', ProductoActivosViewSet)


urlpatterns = [
   path('', include(router.urls)),
]