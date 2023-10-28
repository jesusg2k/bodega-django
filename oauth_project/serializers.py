from rest_framework import serializers

from oauth_project.models.modelos import Permiso, Proyecto, RolProyecto, Miembro, TipoUserStory, Estado, TipoVenta, \
    Cliente, Producto
from django.contrib.auth.models import User


class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = ('id', 'descripcion')

class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ('id', 'descripcion')

class TipoVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoVenta
        fields = ('id', 'descripcion')

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ('id', 'nombre', 'documento')

class ProductoSerializer(serializers.ModelSerializer):
    precios = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = '__all__'

    def get_precios(self, obj):
        return {
            obj.precio_minorista:obj.precio_minorista,
            obj.precio_mayorista:obj.precio_mayorista,
            obj.precio_intermedio:obj.precio_intermedio
        }
        #return [obj.precio_minorista, obj.precio_mayorista, obj.precio_intermedio]

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']

class ProyectoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Proyecto
        fields = ['id', 'nombre_proyecto', 'scrum_master']

class RolProyectoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RolProyecto
        fields = ['id', 'descripcion', 'proyecto']

class MiembroSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Miembro
        fields = ['id', 'rol_en_Proyecto_id', 'cod_user_id']

class TipoUserStorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TipoUserStory
        fields = ['id', 'descripcion', 'estados']