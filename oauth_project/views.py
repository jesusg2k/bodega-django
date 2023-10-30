import datetime

from rest_framework import generics
from django.utils import timezone



import django
import datetime as datetimex
from django.db.models import Q, Count

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail.backends import console
from django.template import loader
from django.template.defaultfilters import length
from django.urls import reverse
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework import viewsets

from oauth_project.serializers import PermisoSerializer, UserSerializer, ProyectoSerializer, RolProyectoSerializer, \
    MiembroSerializer, TipoUserStorySerializer, EstadoSerializer, TipoVentaSerializer, ClienteSerializer, \
    ProductoSerializer, VentaSerializer, DetalleVentaSerializer, CategoriaSerializer
from . import settings

django.setup()

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

from oauth_project.models.modelos import TipoUserStory, PermisoRol, UserStory, Sprint, Profile, Integrante, RolUsuario, \
    RolesSistema, Producto, Cliente, Venta, TipoVenta, Categoria, TipoPago, Devolucion, DetalleVenta, PrecioProducto, \
    EstadoAutorizacion, AutorizacionesRealizadas
from oauth_project.models.modelos import TipoUserStory, PermisoRol, UserStory, Sprint, Profile, Estado, Integrante
from oauth_project.models.modelos import RolProyecto, Equipo, Miembro
from django.http import HttpResponse
import json

from oauth_project.models.modelos import Permiso, Proyecto, Profile

profile = Profile()

from .forms import CreateUserForm

from django.http import Http404


def index(request):
    return redirect("/login")
    ##if not request.user.is_authenticated:
    ##  return redirect("/login")
    ##return html(request, "index")


def html(request, filename):
    """
                Metodo html::

                        def html(request, filename):

                Metodo para renderizar archivos .html que se encuetran en /templates

                Obtiene el archivo mediante el *filename* para despues renderizarlo

                Args:
                    request: Es un objeto de solicitud que recibe con metodo GET
                    filename(string): Es el nombre del archivo a renderizar
                Returns:
                        Render con parámetros *request*, redireccion a *filename.html*, con sus datos personalizados según archivo.
                """
    context = {"filename": filename,
               "collapse": ""}
    print(context)
    if not request.user.is_authenticated and filename == "register":
        return redirect("register")
    if not request.user.is_authenticated and filename != "login":
        return redirect("/login")
    if filename == "logout":
        logout(request)
        return redirect("home")
    if filename == "login" and request.method == "POST":
        print(request.POST)
        username = request.POST.get("username")
        password = request.POST.get("password")
        print('--------')
        try:
            if "@" in username:
                user = User.objects.get(email=username)
            else:
                user = User.objects.get(username=username)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                print('password incorrecta')
                context["error"] = "¡Credenciales inválidas! Revise su usuario, correo o contraseña"
        except ObjectDoesNotExist:
            print('el usuario no existe')
            context["error"] = "¡Credenciales inválidas! Revise su usuario, correo o contraseña"
        print(username, password)
    if filename in ["buttons", "cards"]:
        context["collapse"] = "components"
    if filename in ["utilities-color", "utilities-border", "utilities-animation", "utilities-other"]:
        context["collapse"] = "utilities"
    if filename in ["404", "blank"]:
        context["collapse"] = "pages"
    print(context)
    data_personalizada = {}
    print('---------------')
    print(request)
    print('---------------')
    data = getDataPersonalizada(request, filename)
    data_msg = cargar_msg_session(request)
    return render(request, f"{filename}.html", {"context": context, "data": data, "datamsg": data_msg})


def getDataPersonalizada(request, filename):
    """
                    Metodo getDataPersonalizada::

                            def getDataPersonalizada(request, filename):

                    Metodo para obtener datos personalizados segun archivos .html que se encuetran en /templates

                    Obtiene los datos segun la condicion del nombre mediante el *filename* para despues renderizarlo con html()

                    Args:
                        request: Es un objeto de solicitud que recibe con metodo GET
                        filename(string): Es el nombre del archivo a renderizar
                    Returns:
                            Render con parámetros *request*, redireccion a *filename.html*, con sus datos personalizados según archivo.
                    """
    data = {}
    print("el nombre del archivo es -> " + str(filename))
    if (filename == 'proyectos'):
        id_user = request.user.id
        lista_proyectos = Proyecto.objects.all().filter(
            Q(creado_by=id_user) | Q(rolproyecto__miembro__user_id=id_user) | Q(scrum_master_id=id_user)).order_by('id').annotate(dcount=Count('id'))
        data["lista_proyectos"] = lista_proyectos
        print("se pasaron " + str(length(lista_proyectos)) + " proyectos")

        print(lista_proyectos)

        print(data)
    if (filename == 'ventas-pendientes-modificacion'):
        ventas_rechazadas = Venta.objects.filter(detalleventa__estado_autorizacion=3).distinct()
        ventas_aceptadas = Venta.objects.annotate(
            total_detalles=Count('detalleventa', filter=Q(detalleventa__estado_autorizacion=2))
        ).filter(total_detalles=Count('detalleventa'), detalleventa__estado_autorizacion=2)
        ventas = []
        for v in ventas_aceptadas:
            v.obs_estado = 'AUTORIZACIONES ACEPTADAS'
            if(v.estado.id == 5):
                ventas.append(v)
        for v in ventas_rechazadas:
            v.obs_estado = 'AUTORIZACIONES RECHAZADAS'
            ventas.append(v)
        data['ventas'] = ventas
    if (filename == 'autorizaciones-pendientes'):
        detalles = DetalleVenta.objects.all().filter(estado_autorizacion=1)
        data['autorizaciones_pendientes'] = detalles
    if (filename == 'autorizaciones-realizadas'):
        detalles = AutorizacionesRealizadas.objects.filter(Q(estado_autorizacion=2) | Q(estado_autorizacion=3))
        data['autorizaciones_realizadas'] = detalles
    if (filename == 'devoluciones'):
        devoluciones = Devolucion.objects.all().order_by('id')
        data["devoluciones"] = devoluciones
    if (filename == 'categorias'):
        categorias = Categoria.objects.all().order_by('id')
        data["categorias"] = categorias
    if (filename == 'tipospagos'):
        tipos_pagos = TipoPago.objects.all().order_by('id')
        data["tipospagos"] = tipos_pagos
    if (filename == 'usuarios'):
        usuarios = User.objects.all().order_by('id')
        roles = RolUsuario.objects.all().order_by('id')
        roles_map = {}
        """for user in usuarios:
            map_roles = []
            print('Se busca roles' + user.__str__())
            for rol in roles:
                if rol.usuario.id == user.id:
                    try:
                        map_roles.append(RolesSistema.objects.get(id=rol.id).descripcion)
                        print('Roles encontrados: ')
                        print(map_roles)
                    except:
                        print('no tenia roles')
            roles_map[user.id] = map_roles
            user.roles = map_roles"""

        descripciones_por_usuario = {}
        rol_usuario_list = RolUsuario.objects.select_related('rol', 'usuario')
        # Itera a través de los objetos RolUsuario y construye el diccionario
        for rol_usuario in rol_usuario_list:
            usuario_id = rol_usuario.usuario.id  # Obtenemos el ID del usuario
            descripcion_rol = rol_usuario.rol.descripcion

            # Si el usuario ya está en el diccionario, agregamos la descripción al valor existente
            if usuario_id in descripciones_por_usuario:
                descripciones_por_usuario[usuario_id].append(descripcion_rol)
            else:
                # Si el usuario no está en el diccionario, creamos una nueva entrada con la descripción
                descripciones_por_usuario[usuario_id] = [descripcion_rol]
        print('descripciones de roles por usuario')
        print(descripciones_por_usuario)
        for u in usuarios:
            u.roles = descripciones_por_usuario.get(int(u.id), [])
            print('El usuario -> '+u.__str__()+" tiene -> "+u.roles.__str__())
        data["usuarios"] = usuarios
        print('-------usuarios----------')
        print(usuarios)
        print('-------roles----------')
        print(data)
    if (filename == 'permisos'):
        lista_permisos = Permiso.objects.all()
        data["lista_permisos"] = lista_permisos
        print("se pasaron " + str(length(lista_permisos)) + " permisossss")
        print(data)
    if (filename == 'ventas'):
        ventas = Venta.objects.all()
        data["ventas"] = ventas
        print("se pasaron " + str(length(ventas)) + " ventas")
    if (filename == 'clientes'):
        clientes = Cliente.objects.all()
        data["clientes"] = clientes
        print("se pasaron " + str(length(clientes)) + " clientes")
        print(data)
    if (filename == 'productos'):
        productos = Producto.objects.all()
        data["productos"] = productos
        print("se pasaron " + str(length(productos)) + " productos")
        print(data)
    if (filename == 'tipos-user-story'):
        lista_tipos_user = TipoUserStory.objects.all()
        data["tipos_user_story"] = lista_tipos_user
    if( filename == 'roles-sistema'):
        roles_sistema = RolesSistema.objects.all()
        data["roles_sistema"] = roles_sistema
    id_user = request.user.id
    profile = Profile()
    dic_permiso = profile.get_diccionario_permisos(id_user=id_user)
    ##print(dic_permiso)
    data["permisos"] = dic_permiso
    return data


def registerPage(request):
    """
                        Metodo registerPage::

                                def registerPage(request):

                        Metodo para registar nuevo usuario

                        Obtiene los datos necesarios del request

                        Args:
                            request: Es un objeto de solicitud que recibe con metodo GET
                        Returns:
                                Render con parámetros *request*, redireccion a *register.html* con su contexto
                        """
    if request.method == "POST":
        form_save = UserCreationForm(request.POST)
        if form_save.is_valid():
            form_save.save()
            username = form_save.cleaned_data.get('username')
            password = form_save.cleaned_data('password1')
            first_name = form_save.cleaned_data('nombre')
            last_name = form_save.cleaned_data('apellido')
            email = form_save.cleaned_data('email')
            user = form_save.save(commit=False)
            user.password = make_password("123")
            user.save()
            print('SE ESTA EJECUTANDO')
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email)
            user.password = make_password(password)
            messages.success(request, 'La cuenta fue creada por ' + user + password)
            user = authenticate(username=user, password=password)
            login(request, user)
            return redirect('home')

    form_save = UserCreationForm()
    context = {'form': form_save}
    return render(request, 'register.html', context)


def is_admin(user):
    """
                            Metodo is_admin::

                                    def is_admin(user):

                            Metodo para verificar si es admin/staff

                            Obtiene el dato dentro del parametro user.

                            Args:
                                user: Es un objeto User, que debemos verificar si es admin
                            Returns:
                                    valor boolean que indica si es parte del staff.
                            """
    return user.is_staff


def restriction_process(request, id_proyecto, permiso_verif):
    """
                                Metodo restriction_process::

                                        def restriction_process(request, id_proyecto, permiso_verif):

                                Metodo para verificar si es que tiene permisos necesarios

                                Obtiene el proyecto y el permiso a verificar

                                Args:
                                    request: Es un objeto de solicitud que recibe con metodo GET
                                    id_proyecto (id): Es el id del proyecto a verificar
                                    permiso_verif (string): Es el nombre del permiso a verificar

                                Returns:
                                        valor boolean que indica si tiene permisos suficientes y dirige a 404 en todo caso
                                """
    profile = Profile()
    if not profile.verificar_permiso(request.user.id, id_proyecto, permiso_verif):
        raise Http404


@login_required(login_url='/login/')
def view_mis_proyectos(request):
    """
        Metodo view_mis_proyectos::

                def view_mis_proyectos(request):

        Metodo para renderizar vista proyectos obtiene datos del user del request

        Args:
            request: Es un objeto de solicitud que recibe con metodo GET
        Returns:
                Render de vista de proyectos, con lista de proyectos y mensajes
    """
    id_user = request.user.id
    lista_proyectos = Proyecto.objects.all().filter(creado_by=id_user)
    user = User.objects.get(id=id_user)
    profile = Profile(user)
    profile.get_lista_permisos()
    print(lista_proyectos)
    data_msg = cargar_msg_session(request)
    return render(request, "proyecto/proyecto.html", {"lista_proyectos": lista_proyectos, "datamsg": data_msg})


@login_required(login_url='/login/')
def view_permisos(request):
    """
        Metodo view_permisos::

                def view_permisos(request):

        Metodo para renderizar vista permisos.

        Args:
            request: Es un objeto de solicitud que recibe con metodo GET
        Returns:
                Render de vista de permisos, con lista de permisos y mensajes
    """
    lista_permisos = Proyecto.objects.all()
    print(lista_permisos)
    data_msg = cargar_msg_session(request)
    return render(request, "permisos.html", {"lista_permisos": lista_permisos, "datamsg": data_msg})


@login_required(login_url='/login/')
def view_modificar_proyecto(request):
    """
            Metodo view_modificar_proyecto::

                    def view_modificar_proyecto(request):

            Metodo para facilitar datos de proyecto para modificacion

            Obtiene el *id* del proyecto del parametro recibido *request* con GET

            Obtiene el objeto *proyecto* con el identificador

            Genera un mensaje para mostrar en la vista y envía a través de request.session

            Args:
                request: Es un objeto de solicitud que recibe con metodo GET
            Returns:
                    Render con parámetros *request*, redireccion a *proyecto/modificar-proyecto.html*, el objeto *proyecto* y el mensaje.
            """
    print(request.GET["id"])
    proyecto_id = request.GET["id"]
    proyecto = Proyecto.objects.get(id=proyecto_id)
    data_msg = cargar_msg_session(request)
    return render(request, "proyecto/modificar-proyecto.html", {"proyecto": proyecto, "datamsg": data_msg})


# @login_required(login_url='/login/')

def view_crear_proyecto(request):
    """
            Metodo view_crear_proyecto::

                    def view_crear_proyecto(request):

            Metodo para renderizar formulario crear proyecto, verificando los permisos del usuario que obtiene del request

            Args:
                request: Es un objeto de solicitud que recibe con metodo GET
            Returns:
                    Render de formulario crear proyecto, y mensajes
        """
    if not is_admin(request.user):
        raise Http404
    data_msg = cargar_msg_session(request)
    return render(request, "proyecto/crear-proyecto.html", {"datamsg": data_msg})


@login_required(login_url='/login/')
def view_crear_permiso(request):
    """
                Metodo view_crear_permiso::

                        def view_crear_permiso(request):

                Metodo para renderizar formulario crear permiso, verificando los permisos del usuario que obtiene del request

                Args:
                    request: Es un objeto de solicitud que recibe con metodo GET
                Returns:
                        Render de formulario crear permiso, y mensajes
            """
    data_msg = cargar_msg_session(request)
    return render(request, "permiso/crear-permiso.html", {"datamsg": data_msg})


@login_required(login_url='/login/')
def view_crear_rol(request, id_proyecto_id):
    """
                    Metodo view_crear_rol::

                            def view_crear_rol(request,id_proyecto_id):

                    Metodo para renderizar formulario crear permiso, verificando los permisos del usuario que obtiene del request y de id_proyecto_id

                    Args:
                        request: Es un objeto de solicitud que recibe con metodo GET
                    Returns:
                            Render de formulario crear roles, proyecto y mensajes
                """
    print('VERIFICANDO PERMISOS..... ')
    if not profile.verificar_permiso(request.user.id, id_proyecto_id, 'crear-rol'):
        raise Http404
    return render(request, "rol/crear-rol.html", {"id_proyecto_id": id_proyecto_id, "proyecto_id":id_proyecto_id})

@login_required(login_url='/login/')
def view_crear_rol_sistema(request):
    """
                    Metodo view_crear_rol::

                            def view_crear_rol(request,id_proyecto_id):

                    Metodo para renderizar formulario crear permiso, verificando los permisos del usuario que obtiene del request y de id_proyecto_id

                    Args:
                        request: Es un objeto de solicitud que recibe con metodo GET
                    Returns:
                            Render de formulario crear roles, proyecto y mensajes
                """
    print('VERIFICANDO PERMISOS..... ')
    #if not profile.verificar_permiso(request.user.id, id_proyecto_id, 'crear-rol'):
    #    raise Http404
    return render(request, "rol/crear-rol-sistema.html", {})




@login_required(login_url='/login/')
def view_importar_rol(request, id_proyecto_id):
    """
                Metodo view_importar_rol::

                        def view_importar_rol(request, id_proyecto_id):

                Metodo para facilitar datos de roles por proyecto

                Obtiene todos los roles del sistema y todos los roles del proyecto con el identificador del proyecto *id_proyecto_id*

                Se obtienen los roles disponibles para importar en el proyecto, lod roles que no esten asignados en el proyecto

                Se obtienen los permisos de los roles disponibles

                Args:
                    request: Es un objeto de solicitud que recibe
                    id_proyecto_id (int): El identificador del proyecto
                Returns:
                        Render con parámetros *request*, redireccion a *rol/importar-rol.html*, la lista de *roles_disponibles_json, lsita de *permisos_json*
                """
    rolesSistema = RolProyecto.objects.all()
    rolesProyecto = RolProyecto.objects.filter(proyecto=id_proyecto_id)
    print(rolesSistema)
    print(rolesProyecto)

    listaDescripcion = []
    for rp in rolesProyecto:
        listaDescripcion.append(rp.descripcion)
    print("---------ListaDe Descripcion")
    print(listaDescripcion)
    dicDiferencia = []
    for rs in rolesSistema:
        if not rs.descripcion in listaDescripcion:
            dicDiferencia.append(rs)
    print(dicDiferencia)
    print("---------------------")

    permisos = {}

    rolesDisponibles = []
    for x in dicDiferencia:
        dic = {}
        dic["label"] = x.descripcion
        dic["value"] = x.id
        rolesDisponibles.append(dic)
        permisos_aux = PermisoRol.objects.filter(rol__id=x.id).select_related("permiso")
        dic_p_aux = []
        for p in permisos_aux:
            data = {}
            data['id'] = p.permiso.id
            data['descripcion'] = p.permiso.descripcion
            dic_p_aux.append(data)
        permisos[x.id] = dic_p_aux

    print("-------------RolesDisponibles Diccionario")
    roles_disponibles_json = json.dumps(rolesDisponibles)
    print('-------------------roles_disponibles_json')
    print(roles_disponibles_json)
    print('-------------------')

    permisos_json = json.dumps(permisos)
    print("---------------------")
    print(permisos_json)

    data_msg = cargar_msg_session(request)
    return render(request, "rol/importar-rol.html",
                  {"id_proyecto_id": id_proyecto_id, "roles_disponibles_json": roles_disponibles_json,
                   "permisos_json": permisos_json, "datamsg": data_msg})


@login_required(login_url='/login/')
def view_importar_tipos_user_story(request, id_proyecto_id):
    US_sistema = TipoUserStory.objects.all()
    US_proyecto = Proyecto.objects.get(id=id_proyecto_id).tipos_storys

    lista_US_sistema_estados = []  # es una lista de json
    for a in US_sistema:
        lista_US_sistema_estados.append(a.estados)

    print(lista_US_sistema_estados)  # carga los estados en formato json de los US

    lista_US_proyecto = []
    print("Proyecto US:")
    print(US_proyecto)

    if US_proyecto is not None:
        aDict = json.loads(US_proyecto)  # Transforma la lista json de US del proyecto a un diccionario
        print(aDict)
        for item in aDict:
            print(item['estados'])
            lista_US_proyecto.append(item['estados'])  # obtiene el campo estados,por ende es una lista json

    lista_select = []
    for item_sistema in US_sistema:
        if item_sistema.estados not in lista_US_proyecto and item_sistema.estados not in lista_select:
            print("Importar:")
            print(item_sistema)
            lista_select.append(item_sistema)

    print("LISTA SELECT:")
    print(lista_select)

    tipos_us_Disponibles = []
    for x in lista_select:
        dic = {}
        dic["label"] = "N°" + str(x.id) + " - " + x.descripcion + " - " + x.estados
        dic["value"] = x.id
        tipos_us_Disponibles.append(dic)

    print("LEN RESULTADO:")
    print(len(tipos_us_Disponibles))

    if len(tipos_us_Disponibles) == 0:
        print("LA LISTA ESTA VACIA")
        tipos_us_Disponibles.append(' ')

    print("-------------Tipos US disponibles diccionario")
    tipos_us_disponibles_json = json.dumps(tipos_us_Disponibles)
    print('-------------------tipos us_disponibles_json')
    print(tipos_us_disponibles_json)
    print('-------------------')
    data_msg = cargar_msg_session(request)
    return render(request, "tipostory/importar-tipo-user-story.html",
                  {"id_proyecto_id": id_proyecto_id, "lista_us": tipos_us_disponibles_json, "datamsg": data_msg})


@login_required(login_url='/login/')
def view_modificar_rol(request, id, id_proyecto_id):
    """
               Metodo view_modificar_rol::

                       def view_modificar_rol(request, id_proyecto_id):

               Metodo para facilitar datos de roles por proyecto

               Obtiene la lista de roles por proyecto con el identificador *id* del rol

               Genera un mensaje para mostrar en la vista y envía a través de request.session

               Args:
                   request: Es un objeto de solicitud que recibe
                   id (int): El identificador del rol en el proyecto
                   id_proyecto_id (int): El identificador del proyecto
               Returns:
                       Render con parámetros *request*, redireccion a *rol/modificar-rol.html*, la lista de *rolporproyecto*, el *id_proyecto_id* del proyecto, el *id* del rol por proyecto y el mensaje.
       """
    if not profile.verificar_permiso(request.user.id, id_proyecto_id, 'modificar-rol'):
        raise Http404

    rolporproyecto = RolProyecto.objects.get(id=id)
    data_msg = cargar_msg_session(request)
    return render(request, "rol/modificar-rol.html",
                  {"id": id, "id_proyecto_id": id_proyecto_id, "rolporproyecto": rolporproyecto, "datamsg": data_msg})


def list_task(request):
    lista_de_permisos = Permiso.objects.all()
    print(lista_de_permisos)
    data_msg = cargar_msg_session(request)
    return render(request, "permiso/permiso.html", {"lista_permisos": lista_de_permisos, "datamsg": data_msg})


def get_list_users(request):
    lista_de_permisos = Permiso.objects.all().values()
    response = json.dumps(list(lista_de_permisos))
    print(response)

    return HttpResponse(response)


def vista_form_render(request):
    """
                   vista_form_render::

                           def vista_form_render(request):

                   Es un metodo en desuso que usabamos para probar la visualizacion

                   de un formulario utilizando un formulario en Form IO
   """
    return render(request, "formio/render.html")


def vista_form_render(request):
    """
               vista_form_render::

                       def vista_form_render(request):

               Es un metodo en desuso que usabamos para probar la visualizacion

               de un formulario utilizando un formulario en Form IO
       """
    return render(request, "formio/render2.html")


@login_required(login_url='/login/')
def create_task(request):
    """
           create_task::

                   def create_task(request):

           Es un metodo en desuso que usabamos para probar la creacion

           de un permiso utilizando un formulario en Form IO
   """
    print('va entrar aca -> ')
    print(request.POST)
    # print(request.POST['permiso'])
    # nombre_permiso = request.POST['permiso']
    codigo_permiso = request.POST['data[permasdasdsadsadiso]'];
    codigo_usuario = request.POST['data[usuario]'];
    user = User.objects.get(id=codigo_usuario)
    print(user)
    nombre_permiso = codigo_permiso + " " + codigo_usuario;
    # print(request.POST['data[nombre_de_permiso]'])
    # nombre_permiso = request.POST['data[nombre_de_permiso]']
    # print('se va imprimir el nombre de permiso' + nombre_permiso)
    permiso = Permiso(descripcion=nombre_permiso)
    permiso.save()
    return redirect("/permisos/")


##API
class ProyectoViewSet(viewsets.ModelViewSet):
    """
                       Clase ProyectoViewSet::

                               class ProyectoViewSet(viewsets.ModelViewSet):

                           Es un metodo de serializacion utiliazdo por django rest framework
      """
    queryset = Proyecto.objects.all()
    print(queryset)
    serializer_class = ProyectoSerializer


class RolProyectoViewSet(viewsets.ModelViewSet):
    """
                     Clase RolProyectoViewSet::

                             class RolProyectoViewSet(viewsets.ModelViewSet):

                     Es un metodo de serializacion utiliazdo por django rest framework
    """
    queryset = RolProyecto.objects.all()
    print(queryset)
    serializer_class = RolProyectoSerializer


class MiembroProyectoViewSet(viewsets.ModelViewSet):
    """
                  Clase MiembroProyectoViewSet::

                          class MiembroProyectoViewSet(viewsets.ModelViewSet):

                  Es un metodo de serializacion utiliazdo por django rest framework
      """
    queryset = Miembro.objects.all()
    print(queryset)
    serializer_class = MiembroSerializer


class TipoUserStoryViewSet(viewsets.ModelViewSet):
    """
                Clase TipoUserStoryViewSet::

                        class TipoUserStoryViewSet(viewsets.ModelViewSet):

                Es un metodo de serializacion utiliazdo por django rest framework
    """
    queryset = TipoUserStory.objects.all()
    print(queryset)
    serializer_class = TipoUserStorySerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    """
                    Clase UsuarioViewSet::

                            class UsuarioViewSet(viewsets.ModelViewSet):

                    Es un metodo de serializacion utiliazdo por django rest framework
    """
    User = get_user_model()
    queryset = User.objects.all()
    print(queryset)
    serializer_class = UserSerializer


class TipoVentaViewSet(viewsets.ModelViewSet):
    """
                    Clase UsuarioViewSet::

                            class UsuarioViewSet(viewsets.ModelViewSet):

                    Es un metodo de serializacion utiliazdo por django rest framework
    """
    queryset = TipoVenta.objects.all().order_by('id')
    print(queryset)
    serializer_class = TipoVentaSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    """
                    Clase UsuarioViewSet::

                            class UsuarioViewSet(viewsets.ModelViewSet):

                    Es un metodo de serializacion utiliazdo por django rest framework
    """
    queryset = Cliente.objects.all().order_by('id')
    print(queryset)
    serializer_class = ClienteSerializer

class ProductoActivosViewSet(viewsets.ModelViewSet):
    """
                    Clase UsuarioViewSet::

                            class UsuarioViewSet(viewsets.ModelViewSet):

                    Es un metodo de serializacion utiliazdo por django rest framework
    """
    queryset = Producto.objects.filter(is_active=True, cantidad_stock__gte=1).order_by('id')
    print(queryset)
    serializer_class = ProductoSerializer


class VentaDetallesView(generics.RetrieveAPIView):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
    lookup_field = 'id'  # Esto define el campo que se usará como ID en la URL

    def retrieve(self, request, id=None):
        venta = self.get_object()
        detalles = DetalleVenta.objects.filter(venta=venta)
        detalles_serializer = DetalleVentaSerializer(detalles, many=True)
        return Response(detalles_serializer.data)

class VentasViewSet(viewsets.ModelViewSet):
    """
                    Clase UsuarioViewSet::

                            class UsuarioViewSet(viewsets.ModelViewSet):

                    Es un metodo de serializacion utiliazdo por django rest framework
    """
    queryset = Venta.objects.filter().order_by('id')
    print(queryset)
    serializer_class = VentaSerializer
    lookup_field = 'id'  # Esto define el campo que se usará como ID en la URL

class CategoriaViewSet(viewsets.ModelViewSet):
    """
                    Clase UsuarioViewSet::

                            class UsuarioViewSet(viewsets.ModelViewSet):

                    Es un metodo de serializacion utiliazdo por django rest framework
    """
    queryset = Categoria.objects.filter().order_by('id')
    print(queryset)
    serializer_class = CategoriaSerializer
    lookup_field = 'id'  # Esto define el campo que se usará como ID en la URL


class EstadoViewSet(viewsets.ModelViewSet):
    """
                    Clase UsuarioViewSet::

                            class UsuarioViewSet(viewsets.ModelViewSet):

                    Es un metodo de serializacion utiliazdo por django rest framework
    """
    queryset = Estado.objects.all()
    print(queryset)
    serializer_class = EstadoSerializer


class PermisoViewSet(viewsets.ModelViewSet):
    """
                Clase PermisoViewSet::

                        class PermisoViewSet(viewsets.ModelViewSet):

                Es un metodo de serializacion utiliazdo por django rest framework
    """
    queryset = Permiso.objects.all()
    print(queryset)
    serializer_class = PermisoSerializer


def testing(request):
    mydata = Permiso.objects.all().values()
    template = loader.get_template('template.html')
    context = {
        'mymembers': mydata,
    }
    return HttpResponse(template.render(context, request))




def view_usuarios(request):
    """
            Metodo view_usuarios::

                    def view_usuarios(request):

            Metodo para renderizar el formulario de crear Sprint, se verifica permisos obteniendo usuario del request

            Args:
                request: Es un objeto de solicitud que recibe
            Returns:
                    Render con parámetros request, los datos a renderizar de la vista con la lista de usuarios y el mensaje.
    """
    lista_usuarios = User.objects.all().filter()
    print(lista_usuarios)
    data_msg = cargar_msg_session(request)
    return render(request, "usuario/templates/usuarios.html", {"lista_usuarios": lista_usuarios, "datamsg": data_msg})


def view_modificar_usuario(request, id):
    """
                    Metodo view_modificar_usuario::

                            def view_modificar_usuario(request, id):

                    Metodo para modificar un usuario de estado activo a inactivo

                    Obtiene el objeto user con el *id* del usuario recibido como parametro

                    Se establece como no activo y se guarda en la base de datos

                    Genera un mensaje para mostrar en la vista y envía a través de request.session

                    Args:
                        request: Es un objeto de solicitud que recibe
                        id (int): El identificador del proyecto
                    Returns:
                            Render con parámetros *request*, redireccion a *usuario/modificar-usuario.html*, el *id* del usuario y el mensaje.
                    """
    print(id)
    user_id = id
    usuario = User.objects.get(id=user_id)
    usuario.is_active = False
    usuario.save()
    print(usuario.username)
    data_msg = cargar_msg_session(request)
    return render(request, "usuario/modificar-usuario.html", {"id": id, "datamsg": data_msg})


def view_modificar_equipo_proyecto(request, id):
    """
                   Metodo view_modificar_equipo_proyecto::

                           def view_modificar_equipo_proyecto(request, id):

                   Metodo para facilitar datos de proyecto y equipo

                   Obtiene el objeto proyecto con el *id* del proyecto recibido como parametro

                   Obtiene el equipo del proyecto

                   Genera un mensaje para mostrar en la vista y envía a través de request.session

                   Args:
                       request: Es un objeto de solicitud que recibe
                       id (int): El identificador del proyecto
                   Returns:
                           Render con parámetros *request*, redireccion a *equipo/modificar-equipo.html*, la lista de *equipo*, la lista de *proyecto* y el mensaje.
    """
    if not profile.verificar_permiso(request.user.id, id, 'ver-equipo'):
        raise Http404


    proyecto = Proyecto.objects.get(id=id)
    equipo = Equipo.objects.filter(proyecto=id)
    data_msg = cargar_msg_session(request)
    return render(request, "equipo/modificar-equipo.html",
                  {"equipo": equipo, "proyecto": proyecto, "datamsg": data_msg})


def view_roles_proyecto(request, id_proyecto_id):
    """
       Metodo view_roles_proyecto::

               def view_roles_proyecto(request, id):

       Metodo para facilitar datos de los roles del proyecto a frontend

       Obtiene el objeto proyecto con el *id_proyecto_id*

       Obtiene los roles de ese proyecto con el identificador del proyecto

       Genera un mensaje para mostrar en la vista y envía a través de request.session

       Args:
           request: Es un objeto de solicitud que recibe
           id_proyecto_id (int): El identificador del proyecto
       Returns:
               Render con parámetros *request*, redireccion a *roles-proyecto.html*, la lista de *rolesporproyecto*, el objeto *proyecto*, el *id_proyecto_id* y el mensaje.
    """
    if not profile.verificar_permiso(request.user.id, id_proyecto_id, 'ver-roles'):
        raise Http404


    print("El id del proyecto es -----> " + str(id_proyecto_id))
    rolesporporyecto = RolProyecto.objects.all().filter(proyecto_id=id_proyecto_id)
    print(rolesporporyecto)
    proyecto = Proyecto.objects.get(id=id_proyecto_id)
    msg = ""
    data_msg = cargar_msg_session(request)
    return render(request, "roles-proyecto.html",
                  {"rolesporproyecto": rolesporporyecto, "id_proyecto_id": id_proyecto_id, "proyecto": proyecto,
                   "datamsg": data_msg})


def view_crear_miembros(request, id_proyecto):
    """
                Metodo view_crear_miembros::

                        def view_crear_miembros(request, id):

                Metodo para crear miembros

                Obtiene la lista de miembros de ese proyecto

                Obtiene el objeto proyecto

                Genera un mensaje para mostrar en la vista y envía a través de request.session

                Args:
                    request: Es un objeto de solicitud que recibe
                    id_proyecto (int): El identificador del proyecto
                Returns:
                        Render con parámetros *request*, redireccion a *miembro/crear-miembro.html*, la lista de *miembrosproyecto*, el objeto *proyecto*, el *id_proyecto* y el mensaje.
    """
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'crear-miembro'):
        raise Http404

    print("El id del proyecto es -----> " + str(id_proyecto))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    miembros_proyectos = Miembro.objects.filter(rol__proyecto__id=id_proyecto).select_related("rol", "rol__proyecto",
                                                                                              "user")
    proyecto = Proyecto.objects.get(id=id_proyecto)
    data_msg = cargar_msg_session(request)
    return render(request, "miembro/crear-miembro.html",
                  {"miembrosproyecto": miembros_proyectos, "id_proyecto": id_proyecto, "proyecto": proyecto,
                   "datamsg": data_msg})


def view_crear_miembros(request, id_proyecto):
    """
                                Metodo view_crear_sprint::

                                        def view_crear_sprint(request, id_proyecto):

                                Metodo para renderizar el formulario de crear Sprint

                                A través del parametro id_proyecto se puede obtener los datos del proyecto y miembros correctamente y renderizar

                                Args:
                                    request: Es un objeto de solicitud que recibe
                                    id_proyecto (int): El identificador del Proyecto
                                Returns:
                                        Render con parámetros request, los datos a renderizar de la vista y el mensaje.
                """
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'crear-integrante'):
        raise Http404
    print("El id del proyecto es -----> " + str(id_proyecto))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    miembros_proyectos = Miembro.objects.filter(rol__proyecto__id=id_proyecto).select_related("rol", "rol__proyecto",
                                                                                              "user")
    proyecto = Proyecto.objects.get(id=id_proyecto)
    data_msg = cargar_msg_session(request)
    return render(request, "miembro/crear-miembro.html",
                  {"miembrosproyecto": miembros_proyectos, "id_proyecto": id_proyecto, "proyecto": proyecto,
                   "datamsg": data_msg})


def view_crear_sprint(request, id_proyecto):
    """
                            Metodo view_crear_sprint::

                                    def view_crear_sprint(request, id_proyecto):

                            Metodo para renderizar el formulario de crear Sprint

                            A través del parametro id_proyecto se puede obtener los datos del Proyecto correctamente y renderizar

                            Args:
                                request: Es un objeto de solicitud que recibe
                                id_user_story (int): El identificador del US
                            Returns:
                                    Render con parámetros request, los datos a renderizar de la vista y el mensaje.
            """
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'crear-sprint'):
        raise Http404
    print("El id del proyecto es -----> " + str(id_proyecto))
    proyecto = Proyecto.objects.get(id=id_proyecto)
    data_msg = cargar_msg_session(request)
    return render(request, "sprint/sprints-proyecto.html",
                  {"id_proyecto": id_proyecto, "proyecto": proyecto, "datamsg": data_msg})


def ver_eventos_user_story(request, id_user_story):
    """
                        Metodo ver_eventos_user_story::

                                def ver_eventos_user_story(request, id_id_user_story):

                        Metodo para renderizar la vista de eventos del US

                        A través del parametro id_user_story se puede obtener los datos del US correctamente y renderizar

                        Args:
                            request: Es un objeto de solicitud que recibe
                            id_user_story (int): El identificador del US
                        Returns:
                                Render con parámetros request, los datos a renderizar de la vista y el mensaje.
        """
    print("El id del U.S es -----> " + str(id_user_story))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    user_story = UserStory.objects.get(id=id_user_story)
    eventos = json.loads(user_story.eventos)
    data_msg = cargar_msg_session(request)
    return render(request, "evento/eventos-us.html",
                  {"eventos": eventos, "user_story": user_story,
                   "datamsg": data_msg})


def view_modificar_miembro(request, id_miembro, id_proyecto):
    """
            Metodo view_modificar_miembro::

                    def view_modificar_miembro(request, id_proyecto):

            Metodo para modificar un miembro al un proyecto

            A través del parámetro recibido *id_proyecto*, obtiene la lista de roles de ese proyecto, lo convierte en formato json
            y obtiene el objeto proyecto

            Genera un mensaje para mostrar en la vista y envía a través de request.session

            Args:
                request: Es un objeto de solicitud que recibe
                id_proyecto (int): El identificador del proyecto que recibe
            Returns:
                    Render con parámetros request, redireccion a miembro/crear-miembro.html y la lista de roles_proyecto_json, proyecto y el mensaje.
    """
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'crear-rol'):
        raise Http404

    print("El id del proyecto es -----> " + str(id_proyecto))
    roles_proyectos = RolProyecto.objects.filter(proyecto__id=id_proyecto).select_related("proyecto")
    proyecto = Proyecto.objects.get(id=id_proyecto)

    valuesRolesP = []
    i = 0
    for x in roles_proyectos:
        valuesAux = {}
        valuesAux["label"] = x.descripcion
        valuesAux["value"] = x.id
        valuesRolesP.append(valuesAux)
    print("---------------------")
    print(valuesRolesP)
    roles_proyecto_json = json.dumps(valuesRolesP)
    print("---------------------Lista de roles del proyecto " + str(id_proyecto))
    print(roles_proyecto_json)

    data_msg = cargar_msg_session(request)
    return render(request, "miembro/modificar-miembro.html",
                  {"roles_proyecto_json": roles_proyecto_json,
                   "proyecto": proyecto, "id_miembro": id_miembro,
                   "datamsg": data_msg})


def agregar_us_proyecto(request, id_proyecto):
    """
                Metodo agregar_us_proyecto::

                        def agregar_us_proyecto(request, id):

                Metodo para agregar un User Story a un Proyecto

                A través del parámetro recibido *id_proyecto* que corresponde al identificador del **Proyecto**
                obtiene el objeto *proyecto*

                Genera un mensaje para mostrar en la vista y envía a través de request.session

                Args:
                    request: Es un objeto de solicitud que recibe
                    id_proyecto (int): El identificador del proyecto
                Returns:
                        Render con parámetros request, redireccion a *userstory/crear-userstory.html* y el objeto *proyecto*, el *id_proyecto* y el mensaje.
    """
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'agregar-us-product-backlog'):
        raise Http404


    print("El id del proyecto es -----> " + str(id_proyecto))
    proyecto = Proyecto.objects.get(id=id_proyecto)
    json_lista_storys = {}
    if (proyecto.tipos_storys is not None):
        json_lista_storys = json.loads(proyecto.tipos_storys)
        print(json_lista_storys)
    msg = ""
    data_msg = cargar_msg_session(request)
    return render(request, "userstory/crear-userstory.html",
                  {"proyecto": proyecto, "json_tipos_storys": json_lista_storys, "id_proyecto": id_proyecto,
                   "datamsg": data_msg})


def ver_tablero_kanban(request, id_sprint, nro_tipo_user):
    """
                    Metodo ver_tablero_kanban::

                            def ver_tablero_kanban(request, id_sprint, nro_tipo_user):

                    Metodo para renderizar el tablero kanban

                    A través del parametro id_sprint y nro_tipo_user, se puede obtener los US correctamente y renderizar

                    Args:
                        request: Es un objeto de solicitud que recibe
                        id_sprint (int): El identificador del sprint
                        nro_tipo_user (int): El identificador del tipo US
                    Returns:
                            Render con parámetros request, los datos a renderizar del tablero y el mensaje.
    """
    # if not profile.verificar_permiso(request.user.id, id_proyecto, 'ver-tablero-kanban'):
    #    raise Http404
    sprint = Sprint.objects.get(id=id_sprint)
    proyecto = sprint.proyecto
    id_proyecto = proyecto.id
    print("El id del proyecto es -----> " + str(id_proyecto))
    proyecto = Proyecto.objects.get(id=id_proyecto)

    json_lista_storys = {}
    if (proyecto.tipos_storys is not None):
        json_lista_storys = json.loads(proyecto.tipos_storys)
        print(json_lista_storys)
    json_tipos_storys_sprint = {}
    i = 0
    for tipo_us in json_lista_storys:
        json_tipos_storys_sprint[i] = tipo_us
        i = i + 1
    print('kkkkkkkkkkkkkkkkkkkkkkkkk')
    print(json_tipos_storys_sprint)
    print('kkkkkkkkkkkkkkkkkkkkkkkkk')
    msg = ""
    tipo_user_story = json_lista_storys[nro_tipo_user]
    estados_user = eval(tipo_user_story['estados'])
    estados_id = {}
    i = 0
    for estado in estados_user:
        estados_id[estado] = i
        i = i + 1
    print(estados_id)

    estados_json = {}
    i = 0
    for estado in estados_user:
        dic = {}
        dic['nombre'] = estado
        dic['userstorys'] = []
        estados_json[i] = dic
        i = i + 1
    print(estados_json)

    lista_user_story = UserStory.objects.filter(sprint_asoc__id=id_sprint, tipo_user_story__id=tipo_user_story['id'])

    print('-acaaaa')
    for user_story in lista_user_story:
        # esta funcion toma el estado actual del us,
        # considerando el nombre del estado consigue el id según el diccionario,
        # con lo cual accede al estado del json y
        # accede al subcampo userstory que es un array, y se agrega el user story categorizado por estado.
        print(user_story)
        # user_story['cant_horas_total'] = user_story.cantidad_horas_registras_sprint()
        # user_story['cant_observaciones'] = user_story.cantidad_observaciones_registradas()
        dic = {}
        dic['cant_horas_total_reg'] = user_story.cantidad_horas_registras_sprint()
        dic['cant_horas_sprint'] = user_story.cantidad_horas_registras_sprint(sprint.id)
        dic['cant_total_observaciones'] = user_story.cantidad_observaciones_registradas()
        dic['us'] = user_story
        estados_json[estados_id[user_story.estado]]['userstorys'].append(dic)

    print('-acaaaa')
    print('---------------------------')
    print(estados_json)
    print('---------------------------')

    data_msg = cargar_msg_session(request)
    return render(request, "tablerokanban/tablero-kanban.html",
                  {"proyecto": proyecto, "id_proyecto": id_proyecto,
                   "nro_tipo_user": nro_tipo_user,
                   "tipo_user_story": tipo_user_story,
                   "sprint": sprint,
                   "estados_user": estados_user,
                   "estados_json": estados_json,
                   "tipos_storys_json": json_tipos_storys_sprint,
                   "datamsg": data_msg})


def registrar_actividad_us(request, id_user_story):
    """
                       Metodo registrar_actividad_us::

                             def registrar_actividad_us(request, id_user_story):

                       Metodo para renderizar el formulario para registrar actividad

                       A través del parametro id_user_story, se puede renderizar el formulario con los datos del US.

                       Args:
                           request: Es un objeto de solicitud que recibe
                           id_user_story (int): El identificador del user story

                       Returns:
                               Render con parámetros request, los datos del us a renderizar en el formulario y el mensaje.
           """
    # if not profile.verificar_permiso(request.user.id, id_proyecto, 'ver-tablero-kanban'):
    #    raise Http404
    user_story = UserStory.objects.get(id=id_user_story)
    print('El tipo de nro de story es -> ' + str(user_story.nro_tipo_us()))

    eventos = json.loads(user_story.eventos)
    sprint = user_story.sprint_asoc
    proyecto = user_story.proyecto


    finalizado = 'false'
    if user_story.finalizado:
        finalizado = 'true'
    data_msg = cargar_msg_session(request)
    return render(request, "evento/eventos-us-kanban.html",
                  {"proyecto": proyecto,
                   "sprint": sprint,
                   "user_story": user_story,
                   "eventos": eventos,
                   "finalizado": finalizado,
                   "datamsg": data_msg})


def actualizar_estado_us(request, id_user_story):
    """
                           Metodo actualizar_estado_us::

                                  def actualizar_estado_us(request, id_user_story):

                           Metodo para renderizar el formulario para actualizar estado de US

                           A través del parametro id_user_story, se puede renderizar el formulario con los datos del US.

                           Args:
                               request: Es un objeto de solicitud que recibe
                               id_user_story (int): El identificador del user story

                           Returns:
                                   Render con parámetros request, los datos del us a renderizar en el formulario y el mensaje.
               """
    # if not profile.verificar_permiso(request.user.id, id_proyecto, 'ver-tablero-kanban'):
    #    raise Http404
    user_story = UserStory.objects.get(id=id_user_story)
    tipo_us = user_story.tipo_user_story
    print(tipo_us)
    print(tipo_us.estados)
    estados_user = eval(tipo_us.estados)
    lista_estados = []
    for x in estados_user:
        if x != user_story.estado or user_story.proyecto.scrum_master.id == request.user.id:
            aDict = {}
            aDict["label"] = x
            aDict["value"] = x
            lista_estados.append(aDict)
    estados_lista_json = json.dumps(lista_estados)
    puede_finalizar_tarea = "true"
    if (user_story.proyecto.scrum_master.id == request.user.id):
        puede_finalizar_tarea = "false"


    data_msg = cargar_msg_session(request)
    return render(request, "tablerokanban/actualizar-estado-us.html",
                  {"userstory": user_story,
                   "proyecto": user_story.proyecto,
                   "sprint": user_story.sprint_asoc,
                   "estados": estados_lista_json,
                   "puede_finalizar_tarea": puede_finalizar_tarea,
                   "datamsg": data_msg})


def agregar_sprint_proyecto(request, id_proyecto):
    """
                               Metodo agregar_sprint_proyecto::

                                   def agregar_sprint_proyecto(request, id_proyecto):

                               Metodo para renderizar el formulario para crear un Sprint en un proyecto

                               A través del parametro id_id_proyecto, se puede renderizar el formulario con los datos del Proyecto

                               Args:
                                   request: Es un objeto de solicitud que recibe
                                   id_proyecto (int): El identificador del proyecto

                               Returns:
                                       Render con parámetros request, los datos del proyecto a renderizar en el formulario y el mensaje.
                   """
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'crear-sprint'):
        raise Http404
    print("El id del proyecto es -----> " + str(id_proyecto))
    proyecto = Proyecto.objects.get(id=id_proyecto)
    nro_sprint = Sprint.objects.filter(proyecto__id=id_proyecto).count() + 1
    msg = ""
    data_msg = cargar_msg_session(request)
    return render(request, "sprint/crear-sprint.html",
                  {"proyecto": proyecto,
                   "nro_sprint": nro_sprint,
                   "id_proyecto": id_proyecto,
                   "datamsg": data_msg})


def view_agregar_integrante_sprint(request, id_sprint):
    """
                                   Metodo view_agregar_integrante_sprint::

                                       def view_agregar_integrante_sprint(request, id_sprint):

                                   Metodo para renderizar el formulario para agregar un integrante a un Sprint

                                   A través del parametro id_sprint, se puede renderizar el formulario con los datos del Sprint.

                                   Args:
                                       request: Es un objeto de solicitud que recibe
                                       id_sprint (int): El identificador del sprint

                                   Returns:
                                           Render con parámetros request, los datos del sprint a renderizar en el formulario y el mensaje.
                       """
    sprint = Sprint.objects.get(id=id_sprint)
    # if not profile.verificar_permiso(request.user.id, sprint.proyecto.id, 'agregar-integrante-sprint'):
    #    raise Http404
    print("El id del sprint es -----> " + str(id_sprint))
    miembros = Miembro.objects.filter(rol__proyecto_id=sprint.proyecto.id)
    integrantes_object = json.loads(sprint.equipo)  # string a object
    print("integrantes del sprint en string ## ----- " + str(integrantes_object))

    miembros_disponibles = []
    usuarios = []
    cant_horas = 0

    # se deben conseguir la lista de miembros que no pertenecen en la lista.
    for m in miembros:
        find = False
        for i in integrantes_object:
            id_user = i['id']
            if (m.user_id == id_user):
                find = True
        if not find:
            miembros_disponibles.append(m)
            dic = {}
            dic["label"] = m.user.username
            dic["value"] = m.id
            usuarios.append(dic)

    print("miembros disponibles--------------------")
    print(miembros_disponibles)
    print("usuarios--------------------")
    print(usuarios)
    for i in integrantes_object:
        cant_horas = cant_horas + i['cant_horas']
    sprint.carga_horas_diarias_equipo = cant_horas
    sprint.save()
    msg = ""
    try:
        msg = request.session['msg']
        request.session['msg'] = ''
    except:
        print('no hay session')
    return render(request, "sprint/agregar-integrante-sprint.html",
                  {"sprint": sprint, "miembros_disponibles": usuarios,
                   "msg": msg})


def modificar_sprint_default_proyecto(request, id_sprint, id_proyecto):
    """
                Metodo modificar_sprint_default_proyecto::

                        def modificar_sprint_default_proyecto(request, id_sprint, id_proyecto):

                Metodo para actualizar un sprint creado dentro de un proyecto

                A través del parámetro recibido *id_sprint* que corresponde al identificador del **Sprint**
                obtiene el objeto *sprint*

                Args:
                    request: Es un objeto de solicitud que recibe
                    id_sprint (int): El identificador del sprint
                    id_proyecto (int): El identificador del proyecto
                Returns:
                        Render con parámetros request, redireccion a *sprint/modificar-sprint-default.html* y el objeto *sprint*, *id_proyecto* y el mensaje.
                """
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'crear-sprint'):
        raise Http404
    print("El id del proyecto es -----> " + str(id_proyecto))
    sprint = Sprint.objects.get(id=id_sprint)
    data_msg = cargar_msg_session(request)
    return render(request, "sprint/modificar-sprint-default.html",
                  {
                      "sprint": sprint,
                      "id_proyecto": id_proyecto,
                      "datamsg": data_msg})


def view_actualizar_permisos_rol_proyecto(request, id):
    """
            Metodo view_actualizar_permisos_rol_proyecto::

                    def view_actualizar_permisos_rol_proyecto(request, id):

            Metodo para actualizar los permisos a un rol dentro de un proyecto

            A través del parámetro recibido *id* que corresponde al identificador del **Rol del proyecto**
            obtiene el objeto *rolporproyecto*

            Obiene los permisos que estén activos para ese rol con el *id*

            Obtiene todos los permisos del sistema

            Los permisos son cargados en una lista de diccionarios y convertidos en formato json

            Luego, los permisos activos son cargados en un diccionario y convertidos en formato json

            Genera un mensaje para mostrar en la vista y envía a través de request.session

            Args:
                request: Es un objeto de solicitud que recibe
                id (int): El identificador del rol por proyecto
            Returns:
                    Render con parámetros request, redireccion a *permiso/actualizar-permiso-rol.html* y la lista de *rolporproyecto*, *permisos_json*, *defaultvalues* y el mensaje.
            """

    rolporproyecto = RolProyecto.objects.get(id=id)

    if not profile.verificar_permiso(request.user.id, rolporproyecto.proyecto.id, 'modificar-permisos-rol'):
        raise Http404

    permisos_activados = PermisoRol.objects.all().filter(rol_id=id)
    print('-permisos-activados---')
    print(permisos_activados)
    print('-permisos-activados---')
    permisos = Permiso.objects.all()
    print(permisos)
    valuesPermiso = []
    i = 0
    for x in permisos:
        valuesAux = {}
        valuesAux["label"] = x.descripcion
        valuesAux["value"] = x.id
        valuesAux["shortcut"] = ""
        valuesPermiso.append(valuesAux)
    print("---------------------")
    print(valuesPermiso)
    permisos_json = json.dumps(valuesPermiso)
    print("---------------------")
    print(permisos_json)

    dic = {}
    for x in permisos:
        dic[x.id] = False
    for x in permisos_activados:
        dic[x.permiso.id] = True
    defaultvalues = json.dumps(dic)
    data_msg = cargar_msg_session(request)
    return render(request, "permiso/actualizar-permiso-rol.html",
                  {"rolporproyecto": rolporproyecto, "permisos_json": str(permisos_json),
                   "defaultvalues": defaultvalues, "datamsg": data_msg})


def view_actualizar_tipo_user_story(request, id):
    """
            Metodo view_actualizar_tipo_user_story::

                    def view_actualizar_tipo_user_story(request, id):

            Metodo para actualizar un Tipo de User Story

            A través del parámetro recibido *id* que corresponde al identificador del **Tipo de User Story** obtiene el objeto

            Obiene los estados del Tipo de User Story y lo guarda en una lista de
            diccionarios y lo convierte en formato json


            Genera un mensaje para mostrar en la vista y envía a través de request.session

            Args:
                request: Es un objeto de solicitud que recibe
                id (int): El identificador de Tipo de User Story
            Returns:
                    Render con parámetros request, redireccion a *tipostory/modificar-tipo-story.html* y la lista de *estados_default_values*, *tipo_story* y el mensaje.
            """
    tipo_story = TipoUserStory.objects.get(id=id)
    estados = json.loads(tipo_story.estados)
    print(estados)
    n = len(estados)
    list = []
    print('------n: ' + str(n) + '---------')
    for x in range(n):
        dic = {}
        dic['estado-unique'] = estados[x]
        list.append(dic)
    print(list)
    estados_default_values = json.dumps(list)
    print(estados_default_values)
    data_msg = cargar_msg_session(request)
    return render(request, "tipostory/modificar-tipo-story.html",
                  {"tipo_story": tipo_story, "estados_default_values": estados_default_values, "datamsg": data_msg})


def view_asignar_miembro(request, id_proyecto):
    """
        Metodo view_asignar_miembro::

                def view_asignar_miembro(request, id_proyecto):

        Metodo para asignar un miembro al un proyecto

        A través del parámetro recibido *id_proyecto*, obtiene la lista de roles de ese proyecto, lo convierte en formato json
        y obtiene el objeto proyecto

        Genera un mensaje para mostrar en la vista y envía a través de request.session

        Args:
            request: Es un objeto de solicitud que recibe
            id_proyecto (int): El identificador del proyecto que recibe
        Returns:
                Render con parámetros request, redireccion a miembro/crear-miembro.html y la lista de roles_proyecto_json, proyecto y el mensaje.
        """
    print("El id del proyecto es -----> " + str(id_proyecto))
    roles_proyectos = RolProyecto.objects.filter(proyecto__id=id_proyecto).select_related("proyecto")
    proyecto = Proyecto.objects.get(id=id_proyecto)

    valuesRolesP = []
    i = 0
    for x in roles_proyectos:
        valuesAux = {}
        valuesAux["label"] = x.descripcion
        valuesAux["value"] = x.id
        valuesRolesP.append(valuesAux)
    print("---------------------")
    print(valuesRolesP)
    roles_proyecto_json = json.dumps(valuesRolesP)
    print("---------------------Lista de roles del proyecto " + str(id_proyecto))
    print(roles_proyecto_json)
    data_msg = cargar_msg_session(request)
    return render(request, "miembro/crear-miembro.html",
                  {"roles_proyecto_json": roles_proyecto_json,
                   "proyecto": proyecto,
                   "datamsg": data_msg})


"""
 {
                    "label": "PermisoPorDefecto1",
                    "value": "PermisoPorDefecto1",
                    "shortcut": ""
                },
                {
                    "label": "PermisoPorDefecto2",
                    "value": "PermisoPorDefecto2",
                    "shortcut": ""
                }
"""


def view_miembros_proyecto(request, id_proyecto):
    """
            Metodo view_miembros_proyecto::

                    def view_miembros_proyecto(request, id_proyecto):

            Metodo para facilitar datos al frontend

            A través del parámetro recibido *id_proyecto*, obtiene la lista de miembros del proyecto
            y el objeto proyecto

            Genera un mensaje para mostrar en la vista y envía a través de request.session

            Args:
                request: Es un objeto de solicitud que recibe
                id_proyecto (int): El identificador del proyecto que recibe
            Returns:
                    Render con parámetros request, redireccion a proyectos-miembros.html y la lista de miembrosproyecto, proyecto y el mensaje.
    """
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'ver-miembros'):
        raise Http404

    print("El id del proyecto es -----> " + str(id_proyecto))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    miembros_proyectos = Miembro.objects.filter(rol__proyecto__id=id_proyecto).select_related("rol", "rol__proyecto",
                                                                                              "user")
    proyecto = Proyecto.objects.get(id=id_proyecto)
    data_msg = cargar_msg_session(request)
    return render(request, "proyectos-miembros.html",
                  {"miembrosproyecto": miembros_proyectos, "id_proyecto": id_proyecto, "proyecto": proyecto,
                   "datamsg": data_msg})


def cargar_msg_session(request):
    """
            Metodo cargar_msg_session::

                    def cargar_msg_session(request):

            Permite obtener de la session los mensajes sucess o danger, para indicar al usuario la situación

            Args:
                request: Es un objeto de solicitud que recibe
            Returns:
                    Devuelve un diccionario con los mensajes sucess y danger dentro.
            """
    data = {}
    try:
        msg = request.session['msg']
        request.session['msg'] = ''
        data['msg'] = msg
    except:
        print('no hay session')
    try:
        msg = request.session['msgerror']
        request.session['msgerror'] = ''
        data['msgerror'] = msg
    except:
        print('no hay session')
    return data


def view_equipo_proyecto(request, id_proyecto):
    """
                Metodo view_equipo_proyecto::

                        def view_equipo_proyecto(request, id_proyecto):

                Permite obtener de la session los mensajes sucess o danger, para indicar al usuario la situación

                Args:
                    request: Es un objeto de solicitud que recibe
                Returns:
                        Devuelve un diccionario con los mensajes sucess y danger dentro.
                """
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'ver-miembros'):
        raise Http404
    print("El id del proyecto es -----> " + str(id_proyecto))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    integrantes = Integrante.objects.filter(equipo__proyecto__id=id_proyecto).select_related("integrante")
    proyecto = Proyecto.objects.get(id=id_proyecto)
    data_msg = cargar_msg_session(request)
    return render(request, "equipo/equipo-proyecto.html",
                  {"integrantes_proyecto": integrantes, "id_proyecto": id_proyecto, "proyecto": proyecto,
                   "datamsg": data_msg})


def view_integrantes_proyecto(request, id_proyecto):
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'ver-miembros'):
        raise Http404
    miembros = Miembro.objects.filter(rol__proyecto_id=id_proyecto)
    integrantes_registrados = Integrante.objects.filter(equipo__proyecto_id=id_proyecto)
    print("integrantes----- " + str(integrantes_registrados))

    miembros_disponibles = []
    usuarios = []
    for m in miembros:
        find = False
        for i in integrantes_registrados:
            if (m.user == i.integrante):
                find = True
        if not find:
            miembros_disponibles.append(m)
            dic = {}
            dic["label"] = m.user.username
            dic["value"] = m.id
            usuarios.append(dic)

    print("miembros dispionibles--------------------")
    print(miembros_disponibles)
    print("usuarios--------------------")
    print(usuarios)
    proyecto = Proyecto.objects.get(id=id_proyecto)
    msg = ""
    data_msg = cargar_msg_session(request)
    return render(request, "equipo/crear-integrante.html",
                  {"miembros_disponibles": usuarios, "id_proyecto": id_proyecto, "proyecto": proyecto,
                   "datamsg": data_msg})


def view_producto_backlog(request, id_proyecto):
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'ver-product-backlog'):
        raise Http404
    """
        Metodo view_producto_backlog::

                def view_producto_backlog(request, id_proyecto):

        Metodo para facilitar datos al frontend

        A través del parámetro recibido *id_proyecto*, obtiene la lista de US relacionados al proyecto
        y el objeto proyecto

        Genera un mensaje para mostrar en la vista y envía a través de request.session

        Args:
            request: Es un objeto de solicitud que recibe
            id_proyecto (int): El identificador del proyecto que recibe
        Returns:
                Render con parámetros request, redireccion a productbacklog.html y la lista de Users Storys, proyecto y el mensaje.
        """
    print("El id del proyecto es -----> " + str(id_proyecto))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    users_storys = UserStory.objects.filter(proyecto__id=id_proyecto).select_related("proyecto", "usuario_asignado")
    proyecto = Proyecto.objects.get(id=id_proyecto)

    data = {}
    id_user = request.user.id
    profile2 = Profile()
    dic_permiso = profile2.get_diccionario_permisos(id_user=id_user)
    ##print(dic_permiso)
    data["permisos"] = dic_permiso
    data_msg = cargar_msg_session(request)
    return render(request, "productbacklog.html",
                  {"userstorys": users_storys, "data":data, "proyecto": proyecto, "datamsg": data_msg})



def view_asignacion_us_usuario_sprint(request, id_proyecto, id_sprint):
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'ver-sprint-backlog'):
        raise Http404
    """
        Metodo view_asignacion_us_usuario_sprint::

                def view_asignacion_us_usuario_sprint(request, id_proyecto, id_sprint):

        Metodo para facilitar datos al frontend

        A través del parámetro recibido *id_proyecto*, obtiene la lista de US relacionados al proyecto
        y el objeto proyecto

        Genera un mensaje para mostrar en la vista y envía a través de request.session

        Args:
            request: Es un objeto de solicitud que recibe
            id_proyecto (int): El identificador del proyecto que recibe
            id_sprint (int): El identificador del sprint que recibe
        Returns:
                Render con parámetros request, redireccion a asignacion-us-usuario-sprint.html y la lista de Users Storys, proyecto y el mensaje.
        """
    print("El id del proyecto es -----> " + str(id_proyecto))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    users_storys = UserStory.objects.all().filter(Q(proyecto__id=id_proyecto) & Q(sprint_asoc_id=id_sprint) | Q(sprint_asoc_id=None)).select_related("proyecto", "usuario_asignado")
    users_storys_nuevo = users_storys.values()
    prueba = UserStory.objects.select_related('sprint_asoc').all().values()
    #print("prueba -> "+str(prueba))
    usfinalizados = []
    for object in users_storys_nuevo:
        if( object['sprint_asoc_id'] is not None):
            sprint = Sprint.objects.get(id=object['sprint_asoc_id'])
            print("El sprint asociado es -> "+str(sprint))
            if(sprint.estado.id > 2):
                print("El estado es -> "+str(sprint.estado.descripcion))
                usfinalizados.append(object)
                #eliminar
        print("object -> "+str(object))

    print("users storys del proyecto->"+str(id_proyecto)+" --> "+str(users_storys))
    proyecto = Proyecto.objects.get(id=id_proyecto)
    sprint = Sprint.objects.get(id=id_sprint)

    data = {}
    id_user = request.user.id
    profile2 = Profile()
    dic_permiso = profile2.get_diccionario_permisos(id_user=id_user)
    ##print(dic_permiso)
    data["permisos"] = dic_permiso
    data_msg = cargar_msg_session(request)
    return render(request, "asignacion-us-usuario-sprint.html",
                  {"userstorys": users_storys, "data":data, "proyecto": proyecto, "sprint":sprint , "datamsg": data_msg})



def view_producto_backlog_finalizado(request, id_proyecto):
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'ver-product-backlog'):
        raise Http404
    """
        Metodo view_producto_backlog::

                def view_producto_backlog(request, id_proyecto):

        Metodo para facilitar datos al frontend

        A través del parámetro recibido *id_proyecto*, obtiene la lista de US relacionados al proyecto
        y el objeto proyecto

        Genera un mensaje para mostrar en la vista y envía a través de request.session

        Args:
            request: Es un objeto de solicitud que recibe
            id_proyecto (int): El identificador del proyecto que recibe
        Returns:
                Render con parámetros request, redireccion a productbacklog.html y la lista de Users Storys, proyecto y el mensaje.
        """
    print("El id del proyecto es -----> " + str(id_proyecto))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    users_storys = UserStory.objects.filter(proyecto__id=id_proyecto, finalizado=True).select_related("proyecto", "usuario_asignado")
    proyecto = Proyecto.objects.get(id=id_proyecto)

    data = {}
    id_user = request.user.id
    profile2 = Profile()
    dic_permiso = profile2.get_diccionario_permisos(id_user=id_user)
    #print(dic_permiso)
    data["permisos"] = dic_permiso
    data_msg = cargar_msg_session(request)
    return render(request, "productbacklog.html",
                  {"userstorys": users_storys, "data": data, "proyecto": proyecto, "datamsg": data_msg})
def view_producto_backlog_pendiente(request, id_proyecto):
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'ver-product-backlog'):
        raise Http404
    """
        Metodo view_producto_backlog::

                def view_producto_backlog(request, id_proyecto):

        Metodo para facilitar datos al frontend

        A través del parámetro recibido *id_proyecto*, obtiene la lista de US relacionados al proyecto
        y el objeto proyecto

        Genera un mensaje para mostrar en la vista y envía a través de request.session

        Args:
            request: Es un objeto de solicitud que recibe
            id_proyecto (int): El identificador del proyecto que recibe
        Returns:
                Render con parámetros request, redireccion a productbacklog.html y la lista de Users Storys, proyecto y el mensaje.
        """
    print("El id del proyecto es -----> " + str(id_proyecto))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    users_storys = UserStory.objects.filter(proyecto__id=id_proyecto, finalizado=False).select_related("proyecto", "usuario_asignado")
    proyecto = Proyecto.objects.get(id=id_proyecto)

    data = {}
    id_user = request.user.id
    profile2 = Profile()
    dic_permiso = profile2.get_diccionario_permisos(id_user=id_user)
    #print(dic_permiso)
    data["permisos"] = dic_permiso
    data_msg = cargar_msg_session(request)
    return render(request, "productbacklog.html",
                  {"userstorys": users_storys, "data": data, "proyecto": proyecto, "datamsg": data_msg})
def view_producto_backlog_no_asignado_usuario(request, id_proyecto):
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'ver-product-backlog'):
        raise Http404
    """
        Metodo view_producto_backlog::

                def view_producto_backlog(request, id_proyecto):

        Metodo para facilitar datos al frontend

        A través del parámetro recibido *id_proyecto*, obtiene la lista de US relacionados al proyecto
        y el objeto proyecto

        Genera un mensaje para mostrar en la vista y envía a través de request.session

        Args:
            request: Es un objeto de solicitud que recibe
            id_proyecto (int): El identificador del proyecto que recibe
        Returns:
                Render con parámetros request, redireccion a productbacklog.html y la lista de Users Storys, proyecto y el mensaje.
        """
    print("El id del proyecto es -----> " + str(id_proyecto))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    users_storys = UserStory.objects.filter(proyecto__id=id_proyecto, usuario_asignado=None).select_related("proyecto", "usuario_asignado")
    proyecto = Proyecto.objects.get(id=id_proyecto)

    data = {}
    id_user = request.user.id
    profile2 = Profile()
    dic_permiso = profile2.get_diccionario_permisos(id_user=id_user)
    #print(dic_permiso)
    data["permisos"] = dic_permiso
    data_msg = cargar_msg_session(request)
    return render(request, "productbacklog.html",
                  {"userstorys": users_storys, "data": data, "proyecto": proyecto, "datamsg": data_msg})

def view_producto_backlog_no_asignado_sprint(request, id_proyecto):
    """
            Metodo view_producto_backlog::

                    def view_producto_backlog(request, id_proyecto):

            Metodo para facilitar datos al frontend

            A través del parámetro recibido *id_proyecto*, obtiene la lista de US relacionados al proyecto
            y el objeto proyecto

            Genera un mensaje para mostrar en la vista y envía a través de request.session

            Args:
                request: Es un objeto de solicitud que recibe
                id_proyecto (int): El identificador del proyecto que recibe
            Returns:
                    Render con parámetros request, redireccion a productbacklog.html y la lista de Users Storys, proyecto y el mensaje.
    """
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'ver-product-backlog'):
        raise Http404

    print("El id del proyecto es -----> " + str(id_proyecto))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    users_storys = UserStory.objects.filter(proyecto__id=id_proyecto, sprint_asoc=None).select_related("proyecto", "usuario_asignado")
    proyecto = Proyecto.objects.get(id=id_proyecto)

    data = {}
    id_user = request.user.id
    profile2 = Profile()
    dic_permiso = profile2.get_diccionario_permisos(id_user=id_user)
    #print(dic_permiso)
    data["permisos"] = dic_permiso
    data_msg = cargar_msg_session(request)
    return render(request, "productbacklog.html",
                  {"userstorys": users_storys, "data": data, "proyecto": proyecto, "datamsg": data_msg})

def view_sprint_backlog(request, id_sprint):
    """
            Metodo view_sprint_backlog::

                    def view_producto_backlog(request, id_sprint):

            Metodo para facilitar datos al frontend

            A través del parámetro recibido *id_sprint*, obtiene la lista de US relacionados al sprint
            y el objeto proyecto

            Genera un mensaje para mostrar en la vista y envía a través de request.session

            Args:
                request: Es un objeto de solicitud que recibe
                id_sprint (int): El identificador del sprint que recibe
            Returns:
                    Render con parámetros request, redireccion a sprintbacklog.html y la lista de Users Storys, proyecto y el mensaje.
            """

    sprint = Sprint.objects.get(id=id_sprint)
    if not profile.verificar_permiso(request.user.id, sprint.proyecto.id, 'ver-sprint-backlog'):
        raise Http404


    print("El id del sprint es -----> " + str(id_sprint))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    users_storys = UserStory.objects.filter(proyecto__id=sprint.proyecto.id, sprint_asoc_id=id_sprint).select_related("proyecto", "usuario_asignado")
    proyecto = Proyecto.objects.get(id=sprint.proyecto.id)

    data = {}
    id_user = request.user.id
    profile2 = Profile()
    dic_permiso = profile2.get_diccionario_permisos(id_user=id_user)
    #print(dic_permiso)
    data["permisos"] = dic_permiso

    data_msg = cargar_msg_session(request)
    return render(request, "sprintbacklog.html",
                  {"userstorys": users_storys, "sprint": sprint, "proyecto": proyecto, "datamsg": data_msg,
                   "data": data})


def view_sprint_backlog_finalizado(request, id_sprint):
    """
           Metodo view_sprint_backlog::

                   def view_producto_backlog(request, id_sprint):

           Metodo para facilitar datos al frontend

           A través del parámetro recibido *id_sprint*, obtiene la lista de US relacionados al sprint
           y el objeto proyecto

           Genera un mensaje para mostrar en la vista y envía a través de request.session

           Args:
               request: Es un objeto de solicitud que recibe
               id_sprint (int): El identificador del sprint que recibe
           Returns:
                   Render con parámetros request, redireccion a sprintbacklog.html y la lista de Users Storys, proyecto y el mensaje.
           """
    sprint = Sprint.objects.get(id=id_sprint)
    if not profile.verificar_permiso(request.user.id, sprint.proyecto.id, 'ver-sprint-backlog'):
        raise Http404


    print("El id del sprint es -----> " + str(id_sprint))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    users_storys = UserStory.objects.filter(proyecto__id=sprint.proyecto.id, sprint_asoc_id=id_sprint, finalizado=True).select_related("proyecto", "usuario_asignado")
    proyecto = Proyecto.objects.get(id=sprint.proyecto.id)

    data = {}
    id_user = request.user.id
    profile2 = Profile()
    dic_permiso = profile2.get_diccionario_permisos(id_user=id_user)
    #print(dic_permiso)
    data["permisos"] = dic_permiso

    data_msg = cargar_msg_session(request)
    return render(request, "sprintbacklog.html",
                  {"userstorys": users_storys, "sprint": sprint, "proyecto": proyecto, "datamsg": data_msg,
                   "data": data})

def view_sprint_backlog_pendiente(request, id_sprint):
    """
            Metodo view_sprint_backlog::

                    def view_producto_backlog(request, id_sprint):

            Metodo para facilitar datos al frontend

            A través del parámetro recibido *id_sprint*, obtiene la lista de US relacionados al sprint
            y el objeto proyecto

            Genera un mensaje para mostrar en la vista y envía a través de request.session

            Args:
                request: Es un objeto de solicitud que recibe
                id_sprint (int): El identificador del sprint que recibe
            Returns:
                    Render con parámetros request, redireccion a sprintbacklog.html y la lista de Users Storys, proyecto y el mensaje.
            """
    sprint = Sprint.objects.get(id=id_sprint)
    if not profile.verificar_permiso(request.user.id, sprint.proyecto.id, 'ver-sprint-backlog'):
        raise Http404


    print("El id del sprint es -----> " + str(id_sprint))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    users_storys = UserStory.objects.filter(proyecto__id=sprint.proyecto.id, sprint_asoc_id=id_sprint, finalizado=False).select_related("proyecto", "usuario_asignado")
    proyecto = Proyecto.objects.get(id=sprint.proyecto.id)

    data = {}
    id_user = request.user.id
    profile2 = Profile()
    dic_permiso = profile2.get_diccionario_permisos(id_user=id_user)
    #print(dic_permiso)
    data["permisos"] = dic_permiso

    data_msg = cargar_msg_session(request)
    return render(request, "sprintbacklog.html",
                  {"userstorys": users_storys, "sprint": sprint, "proyecto": proyecto, "datamsg": data_msg,
                   "data": data})

def view_sprint_backlog_sin_usuario_asignado(request, id_sprint):
    """
            Metodo view_sprint_backlog::

                    def view_producto_backlog(request, id_sprint):

            Metodo para facilitar datos al frontend

            A través del parámetro recibido *id_sprint*, obtiene la lista de US relacionados al sprint
            y el objeto proyecto

            Genera un mensaje para mostrar en la vista y envía a través de request.session

            Args:
                request: Es un objeto de solicitud que recibe
                id_sprint (int): El identificador del sprint que recibe
            Returns:
                    Render con parámetros request, redireccion a sprintbacklog.html y la lista de Users Storys, proyecto y el mensaje.
            """
    sprint = Sprint.objects.get(id=id_sprint)
    if not profile.verificar_permiso(request.user.id, sprint.proyecto.id, 'ver-sprint-backlog'):
        raise Http404


    print("El id del sprint es -----> " + str(id_sprint))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    users_storys = UserStory.objects.filter(proyecto__id=sprint.proyecto.id, sprint_asoc_id=id_sprint, usuario_asignado=None).select_related("proyecto", "usuario_asignado")
    proyecto = Proyecto.objects.get(id=sprint.proyecto.id)

    data = {}
    id_user = request.user.id
    profile2 = Profile()
    dic_permiso = profile2.get_diccionario_permisos(id_user=id_user)
    #print(dic_permiso)
    data["permisos"] = dic_permiso

    data_msg = cargar_msg_session(request)
    return render(request, "sprintbacklog.html",
                  {"userstorys": users_storys,"sprint":sprint, "proyecto": proyecto, "datamsg": data_msg, "data":data})


def view_sprints_proyecto(request, id_proyecto):
    """
                                   Metodo view_sprints_proyecto::

                                           def view_sprints_proyecto(request,id_proyecto)::

                                   Metodo para renderizar el ver la lista de spirints del proyecto obtenidos de id_id_proyecto.

                                   A través del parametro id_proyecto se puede renderizar la vista con los datos correspondientes a cada uno.

                                   Args:
                                       request: Es un objeto de solicitud que recibe
                                       id_user_story (int): El identificador del US
                                   Returns:
                                           Render con parámetros request, redireccion a spints/sprint-proyecto.html.
                                   """
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'ver-sprint'):
        raise Http404

    print("El id del proyecto es -----> " + str(id_proyecto))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    sprints = Sprint.objects.filter(proyecto__id=id_proyecto).select_related("proyecto")
    # 4 es el estado cancelado
    cant_sprints_pendientes = Sprint.objects.filter(proyecto__id=id_proyecto,
                                                    estado__sprint__proyecto_id__lte=3).select_related(
        "proyecto").count()
    print('la cantidad de sprints pendientes son-> activos son: ' + str(cant_sprints_pendientes))
    proyecto = Proyecto.objects.get(id=id_proyecto)
    print("Entro en el primer metodo de view_sprints_proyecto")
    data_msg = cargar_msg_session(request)
    return render(request, "/sprints/" + str(id_proyecto),
                  {"sprints": sprints, "proyecto": proyecto, "cant_sprints_pendientes": cant_sprints_pendientes,
                   "datamsg": data_msg})


def view_tipos_story_proyecto(request, id_proyecto):
    """
          Metodo view_tipos_story_proyecto::

                  def view_tipos_story_proyecto(request,id_proyecto)::

          Metodo para renderizar el ver la lista de tipos_users_story del proyecto obtenidos de id_proyecto.

          A través del parametro id_proyecto se puede renderizar la vista con los datos correspondientes a cada uno.

          Args:
              request: Es un objeto de solicitud que recibe
              id_user_story (int): El identificador del US
          Returns:
                  Render con parámetros request, redireccion a tipostory/tipo-story-proyecto.html.
    """
    print("El id del proyecto es -----> " + str(id_proyecto))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    proyecto = Proyecto.objects.get(id=id_proyecto)
    msg = ""
    json_lista = {}
    if (proyecto.tipos_storys is not None):
        print(proyecto.tipos_storys)
        json_lista = json.loads(proyecto.tipos_storys)
        print('se recargo la lista de storys')
    print(json_lista)
    data_msg = cargar_msg_session(request)
    return render(request, "tipostory/tipo-story-proyecto.html",
                  {"tipos_story": json_lista, "proyecto": proyecto, "datamsg": data_msg, "id_proyecto_id": id_proyecto})


def view_sprints_proyecto(request, id_proyecto):
    """
                               Metodo view_sprints_proyecto::

                                       def view_sprints_proyecto(request,id_proyecto)::

                               Metodo para renderizar el ver la lista de spirints del proyecto obtenidos de id_id_proyecto.

                               A través del parametro id_proyecto se puede renderizar la vista con los datos correspondientes a cada uno.

                               Args:
                                   request: Es un objeto de solicitud que recibe
                                   id_user_story (int): El identificador del US
                               Returns:
                                       Render con parámetros request, redireccion a spints/sprint-proyecto.html.
                               """
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'ver-sprint'):
        raise Http404

    print("El id del proyecto es -----> " + str(id_proyecto))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    sprints_lista = Sprint.objects.filter(proyecto__id=id_proyecto).select_related("proyecto")
    # 4 es el estado cancelado
    cant_sprints_pendientes = Sprint.objects.filter(proyecto__id=id_proyecto,
                                                    estado__sprint__proyecto_id__lte=3).select_related(
        "proyecto").count()
    print('la cantidad de sprints pendientes son--> activos son: ' + str(cant_sprints_pendientes))
    print("Entro en el segundo metodo de view_sprints_proyecto")
    proyecto = Proyecto.objects.get(id=id_proyecto)
    msg = ""

    tipos_user_storys_proyectos = {}
    for x in sprints_lista:
        tipos_json = json.loads(x.tipos_storys)
        tipos_aux = []
        for k in tipos_json:
            tipos_aux.append(k["nombre"])
        tipos_user_storys_proyectos[x.id] = tipos_aux
    print('----------------------Tipo US')
    print(tipos_user_storys_proyectos)
    print('----------------------')
    exists_sprint_activo = Sprint.objects.filter(proyecto__id=id_proyecto, estado=2).exists()
    print("Existe Sprint Activo? " + str(exists_sprint_activo))
    sprints = Sprint.objects.filter(proyecto__id=id_proyecto).select_related("proyecto")
    equipo = Equipo.objects.filter(proyecto__id=id_proyecto).select_related("proyecto")
    print("El equipo del sprint es -> " + str(equipo))
    print("Sprint estado capacidad total del equipo -> " + str(sprints))
    permisos = profile.get_diccionario_permisos(id_user=request.user.id)
    print("permisos es -> " + str(permisos))
    data_msg = cargar_msg_session(request)
    data = {}
    dic_permiso = profile.get_diccionario_permisos(id_user=request.user.id)
    #print(dic_permiso)
    data["permisos"] = dic_permiso

    return render(request, "sprint/sprints-proyecto.html",
                  {"sprints": sprints, "tipos_storys": tipos_user_storys_proyectos,
                   "proyecto": proyecto, "cant_sprints_pendientes": cant_sprints_pendientes,
                   "permisos": permisos, "exists_sprint_activo": exists_sprint_activo, "equipo_proyecto": equipo[0], "data":data,
                   "datamsg": data_msg})


def view_proyecto_burdown_chart(request, id_proyecto):
    """
                               Metodo view_proyecto_burdown_chart::

                                       def view_proyecto_burdown_chart(request,id_proyecto)::

                               Metodo para renderizar el ver del proyecto obtenidos de id_id_proyecto.
                               recibe el id proyecto y consigue todos los US
                               Obtiene la fecha de los proyectos y de los US
                               Con esa informacion se obtienen los datos necesarios para construir el grafico del burdownchart

                               Args:
                                   request: Es un objeto de solicitud que recibe
                                   id_proyecto (int): El identificador del proyecto
                               Returns:
                                       Render con parámetros request, redireccion a una vista de burdown chart
                               """

    proyecto = Proyecto.objects.get(id=id_proyecto)
    us_story = UserStory.objects.filter(proyecto__id=id_proyecto)

    primera_fecha = proyecto.fecha_inicio
    fecha_ultima_chart = proyecto.fecha_fin

    print('---------------------------------------------------------')
    for us in us_story:
        if fecha_ultima_chart is None:
            fecha_ultima_chart = us.ultima_fecha()
        if fecha_ultima_chart < us.ultima_fecha():
            fecha_ultima_chart = us.ultima_fecha()
        print(us)
        print(us.primera_fecha())
        print(us.ultima_fecha())
    print('---------------------------------------------------------')

    print('primera fecha es ->')
    print(primera_fecha)

    print('ultima fecha es -> ')
    print(fecha_ultima_chart)

    print('cantidad tareas totales ->')
    print(str(len(us_story)))
    cant_total_us = str(len(us_story))

    us_story_finalizado = UserStory.objects.filter(proyecto__id=id_proyecto, finalizado=True)
    print('cantidad tareas terminadas ->')
    print(str(len(us_story_finalizado)))

    cant_dias = (fecha_ultima_chart.date() - primera_fecha).days
    print('La cantidad de dias del grafico es -> '+str(cant_dias))


    dic_graf = []
    for x in range(cant_dias+1):
        dic = {}
        primera_fecha_tmp = primera_fecha + datetimex.timedelta(days=int(x))
        dic['date'] = primera_fecha_tmp
        dic['cant_tareas_total'] = cant_total_us
        dic['cant_tareas_realizadas'] = 0
        dic['cant_tareas_pendientes'] = int(cant_total_us)
        dic['sprint'] = 0
        print(primera_fecha_tmp)
        dic_graf.append(dic)


    for u in us_story_finalizado:
        print("ID-> "+str(u.id)+ " - Ult. Fecha: " +str(u.ultima_fecha()))

    print(dic_graf)
    print('------------date---------------')
    i = 0
    for x in dic_graf:
        print(str(x['date']))
        for u in us_story_finalizado:
            print(str(u.id)+ " - " +str(u.ultima_fecha()))
            if u.ultima_fecha().date() <= x['date']:
                print('se resta en ->'+str(i))
                dic_graf[i]['cant_tareas_realizadas'] = dic_graf[i]['cant_tareas_realizadas'] + 1
                dic_graf[i]['cant_tareas_pendientes'] = dic_graf[i]['cant_tareas_pendientes'] - 1
        i = i + 1


    i = 0
    for x in dic_graf:
        print(str(x['date']))
        for u in us_story:
            print(str(u.id) + " - " + str(u.ultima_fecha()))
            if u.ultima_fecha().date() <= x['date']:
                if u.sprint_asoc is not None:
                    if u.sprint_asoc.id < x['sprint'] or x['sprint'] == 0:
                        dic_graf[i]['sprint'] = u.sprint_asoc.id
        i = i + 1

    sprints = Sprint.objects.filter(proyecto__id = id_proyecto)

    for sp in sprints:
        i = 0
        for x in dic_graf:
            if sp.fecha_inicio <= x['date']:
                dic_graf[i]['sprint'] = sp.id
            i = i + 1
    print('------------date---------------')

    labels = []
    data = []
    i = 0
    for x in dic_graf:
        i = i + 1
        text = "Día:"+str(i)+"\n"+ str(x['date'])[5:] + "\n Sprint N° "+str(x['sprint'])
        labels.append(text)
        data.append(x['cant_tareas_pendientes'])
        print('Date-> '+str(x['date'])+' Sprint: N°'+str(x['sprint'])+" Cant Total: "+str(x['cant_tareas_total'])+ "Cant Pendiente: "+str(x['cant_tareas_pendientes']))

    velocity = {}
    for sp in sprints:
        velocity[sp.id] = 0

    for us in us_story_finalizado:
        if us.finalizado == True and us.sprint_asoc is not None:
            velocity[us.sprint_asoc.id] = velocity[us.sprint_asoc.id] +1

    labels_ve = []
    data_ve = []
    for k,v in velocity.items():
        labels_ve.append("Sprint N° "+str(k))
        data_ve.append(v)
    data_msg = cargar_msg_session(request)
    return render(request, "proyecto/burndownchart.html",
                  {
                       "proyecto": proyecto,
                       "datamsg": data_msg,
                       "labels": labels,
                       "labels_v": labels_ve,
                      "data_v":data_ve,
                       "data": data
                   })


def asignar_usuario_user_story(request, id_user_story, id_sprint):
    """
                            Metodo asignar_usuario_user_story::

                                    def asignar_usuario_user_story(request,id_user_story)::

                            Metodo para renderizar el formulario para asignar US.

                            A través del parametro id_user_story se puede renderizar el formulario con los datos correspondientes a cada uno.

                            Args:
                                request: Es un objeto de solicitud que recibe
                                id_user_story (int): El identificador del US
                            Returns:
                                    Render con parámetros request, redireccion a sprint/asignar_usuario_productbacklog.html
                            """
    userstory = UserStory.objects.get(id=id_user_story)
    miembros = Miembro.objects.filter(rol__proyecto_id=userstory.proyecto.id)
    lista_usuario = []

    for x in miembros:
        aDict = {}
        aDict["label"] = x.user.username
        aDict["value"] = x.user.id
        lista_usuario.append(aDict)
    print("---------------------")
    print(lista_usuario)
    usuario_user_story_json = json.dumps(lista_usuario)
    sprint = Sprint.objects.get(id=id_sprint)
    data_msg = cargar_msg_session(request)
    return render(request, "asignar_usuario_productbacklog.html",
                  {"usuarios": usuario_user_story_json,
                   "sprint": sprint,
                   "user_story": userstory,
                   "datamsg": data_msg})


def asignar_usuario_user_story_sprintbackog(request, id_user_story):
    """
                        Metodo asignar_usuario_user_story_sprintbackog::

                                def asignar_usuario_user_story_sprintbackog(request,id_user_story)::

                        Metodo para renderizar el formulario para asignar sprint a US

                        A través del parametro id_user_story se puede renderizar el formulario con los datos correspondientes a cada uno.

                        Args:
                            request: Es un objeto de solicitud que recibe
                            id_user_story (int): El identificador del US
                        Returns:
                                Render con parámetros request, redireccion a sprint/asignar_usuario_sprintbacklog.html
                        """
    userstory = UserStory.objects.get(id=id_user_story)
    miembros = Miembro.objects.filter(rol__proyecto_id=userstory.proyecto.id)
    lista_usuario =[]

    for x in miembros:
        aDict = {}
        aDict["label"] = x.user.username
        aDict["value"] = x.user.id
        lista_usuario.append(aDict)
    print("---------------------")
    print(lista_usuario)
    usuario_user_story_json = json.dumps(lista_usuario)
    data_msg = cargar_msg_session(request)
    return render(request, "asignar_usuario_sprintbacklog.html",
                  {"usuarios": usuario_user_story_json,
                   "sprint": userstory.sprint_asoc,
                   "user_story": userstory,
                   "datamsg":data_msg})


def view_asignar_sprint_user_story(request, id_user_story, id_sprint):
    """
                    Metodo view_asignar_sprint_user_story::

                            def view_asignar_sprint_user_story(request,id_user_story)::

                    Metodo para renderizar el formulario para asignar sprint a US

                    A través del parametro id_user_story se puede renderizar el formulario con los datos correspondientes a cada uno.

                    Args:
                        request: Es un objeto de solicitud que recibe
                        id_user_story (int): El identificador del US
                    Returns:
                            Render con parámetros request, redireccion a sprint/asignar_sprint_user_story.html
                    """
    user_story = UserStory.objects.get(id=id_user_story)
    #sprints = Sprint.objects.filter(proyecto_id=user_story.proyecto.id).order_by("-id")
    sprint = Sprint.objects.get(id=id_sprint)
    print("Sprint del proyecto -> "+str(sprint))
    lista_sprints = []

    #for x in sprints:
    aDict = {}
    aDict["label"] = str(sprint.id) + " - " + sprint.descripcion + " - " + sprint.estado.descripcion
    aDict["value"] = sprint.id
    lista_sprints.append(aDict)
    print("---------------------")
    print(lista_sprints)
    sprint_user_story_json = json.dumps(lista_sprints)
    data_msg = cargar_msg_session(request)
    return render(request, "userstory/asignar_sprint_user_story.html",
                  {"sprints": sprint_user_story_json, "user_story": user_story, "datamsg": data_msg})


def view_modificar_integrante_proyecto(request, id_integrante, id_proyecto):
    """
            Metodo view_modificar_integrante_proyecto::

                    def view_modificar_integrante_proyecto(request, id_integrante, id_proyecto)::

            Metodo para renderizar el formulario para registrar actividad

            A través del parametro id_integrante y id_proyecto, se puede renderizar el formulario con los datos correspondientes a cada uno.

            Args:
                request: Es un objeto de solicitud que recibe
                id_proyecto (int): El identificador del id_integrante que recibe
                id_integrante (int): El identificador del id_proyecto que recibe
            Returns:
                    Render con parámetros request, redireccion a sprint/equipo-sprint.html, datos de integrante, el proyecto y el mensaje.
            """
    print(request.POST)
    print("El ID del integrante es -> " + str(id_integrante))
    data_msg = cargar_msg_session(request)
    return render(request, "equipo/modificar-integrante.html",
                  {"id_integrante": id_integrante, "id_proyecto": id_proyecto, "datamsg": data_msg})




def view_equipo_sprint(request, id_sprint):
    """
                Metodo view_equipo_sprint::

                        def view_equipo_sprint(request, id_sprint)::

                Metodo para renderizar la vista para ver el equipo del sprint

                A través del parametro id_sprint se puede renderizar la vista con los datos correspondientes del equipo.

                Args:
                    request: Es un objeto de solicitud que recibe
                    id_sprint (int): El identificador del Sprint que recibe
                Returns:
                        Render con parámetros request, redireccion a sprint/equipo-sprint.html, datos de integrante, el proyecto y el mensaje.
    """
    print("El id del Sprint es -----> " + str(id_sprint))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    sprint = Sprint.objects.get(id=id_sprint)
    msg = ""
    json_lista = {}
    if (sprint.equipo is not None):
        print(sprint.equipo)
        json_lista = json.loads(sprint.equipo)
        print('se recargo la lista de equipo')
    print(json_lista)
    data_msg = cargar_msg_session(request)
    permisos = profile.get_diccionario_permisos(id_user=request.user.id)
    print("permisos es -> " + str(permisos))
    data_msg = cargar_msg_session(request)
    data = {}
    dic_permiso = profile.get_diccionario_permisos(id_user=request.user.id)
    #print(dic_permiso)
    data["permisos"] = dic_permiso
    return render(request, "sprint/equipo-sprint.html",
                  {"equipos": json_lista, "sprint": sprint, "data":data, "permisos":permisos,"datamsg": data_msg})

def view_informe_sprint_actual(request, id_sprint):
    """
                    view_informe_sprint_actual(request, id_sprint)::

                            def view_informe_sprint_actual(request, id_sprint)::

                    Metodo para renderizar la vista para ver el informe del sprint

                    A través del parametro id_sprint se puede renderizar la vista con los datos correspondientes del Sprint.

                    Args:
                        request: Es un objeto de solicitud que recibe
                        id_sprint (int): El identificador del Sprint que recibe
                    Returns:
                            Render con parámetros request, redireccion a sprint/informe-sprint.html, con todos sus datos para el informe y el mensaje.
        """
    sprint = Sprint.objects.get(id=id_sprint)
    datos = sprint.get_datos_informe()
    data = cargar_msg_session(request)
    return render(request, "sprint/informe-sprint.html",
                  {"sprint": sprint,
                   "datos": datos,
                   "datamsg": data})

def view_informe_sprint_historico(request, id_sprint):
    """
                        view_informe_sprint_historico(request, id_sprint)::

                                def view_informe_sprint_historico(request, id_sprint)::

                        Metodo para renderizar la vista para ver el informe del sprint

                        A través del parametro id_sprint se puede renderizar la vista con los datos correspondientes del Sprint.

                        Args:
                            request: Es un objeto de solicitud que recibe
                            id_sprint (int): El identificador del Sprint que recibe
                        Returns:
                                Render con parámetros request, redireccion a sprint/informe-sprint.html, con todos sus datos para el informe y el mensaje.
            """
    sprint = Sprint.objects.get(id=id_sprint)
    json_historico = sprint.json_informe_historico_finalizacion
    datos = json.loads(json_historico)
    data = cargar_msg_session(request)
    return render(request, "sprint/informe-sprint.html",
                  {"sprint": sprint,
                   "datos": datos,
                   "datamsg": data})


def actualizar_cliente(request, id):
    print("El id del cliente es -----> " + str(id))
    cliente = Cliente.objects.get(id=id)
    data_msg = cargar_msg_session(request)
    return render(request, "cliente/modificar-cliente.html",
                  {
                   "cliente": cliente, "id_cliente": id,
                   "datamsg": data_msg}
                  )


def actualizar_tipo_pago(request, id):
    print("El id de la tippago es -----> " + str(id))
    tipo_pago = TipoPago.objects.get(id=id)
    data_msg = cargar_msg_session(request)
    return render(request, "tipo_pago/modificar_tipo_pago.html",
                  {
                   "tipo_pago": tipo_pago, "id_tipo_pago": id,
                   "datamsg": data_msg}
                  )


def actualizar_categoria(request, id):
    print("El id de la categoria es -----> " + str(id))
    categoria = Categoria.objects.get(id=id)
    data_msg = cargar_msg_session(request)
    return render(request, "categoria/modificar_categoria.html",
                  {
                   "categoria": categoria, "id_categoria": id,
                   "datamsg": data_msg}
                  )

def actualizar_producto(request, id):
    print("El id del producto es -----> " + str(id))
    producto = Producto.objects.get(id=id)
    data_msg = cargar_msg_session(request)
    return render(request, "producto/modificar-producto.html",
                  {
                   "IP_SERVER": settings.IP_SERVER,
                   "producto": producto, "id_producto": id,
                   "datamsg": data_msg}
                  )

def ver_lista_precios(request, id):
    print("El id del producto es -----> " + str(id))
    producto = Producto.objects.get(id=id)
    data_msg = cargar_msg_session(request)
    return render(request, "producto/lista_precios.html",
                  {
                   "producto": producto,"precios": producto.obtener_precios(),
                   "id_producto": id,
                   "datamsg": data_msg}
                  )

def actualizar_rol_usuario(request, id_usuario):
    print("El id del usuario es -----> " + str(id_usuario))
    user = User.objects.get(id= id_usuario)
    roles_disponibles_para_usuarios = RolesSistema.objects.all()
    valuesRolesP = []
    i = 0
    for x in roles_disponibles_para_usuarios:
        valuesAux = {}
        valuesAux["label"] = x.descripcion
        valuesAux["value"] = x.id
        valuesRolesP.append(valuesAux)
    print("---------------------")
    print(valuesRolesP)
    roles_proyecto_json = json.dumps(valuesRolesP)
    data_msg = cargar_msg_session(request)
    return render(request, "rolusuario/agregar-rol-usuario.html",
                  {"roles_proyecto_json": roles_proyecto_json,
                   "usuario": id_usuario, "user": user,  "usuario_id": id_usuario,
                   "datamsg": data_msg})

def form_crear_usuario_sistema(request):
    data_msg = cargar_msg_session(request)
    return render(request, "usuario/crear-usuario-sistema.html",
                  {
                   "datamsg": data_msg})

def form_crear_categoria(request):
    data_msg = cargar_msg_session(request)
    return render(request, "categoria/crear-categoria.html",
                  {
                   "datamsg": data_msg})

def form_crear_precio(request, id):
    data_msg = cargar_msg_session(request)
    producto = Producto.objects.get(id=id)
    return render(request, "producto/crear-precio.html",
                  {
                      "producto": producto,
                      "id_producto": producto,
                   "datamsg": data_msg})

def form_modificar_precio(request, id):
    data_msg = cargar_msg_session(request)
    precio = PrecioProducto.objects.get(id=id)
    return render(request, "producto/modificar-precio.html",
                  {
                      "precio": precio,
                      "producto": precio.producto,
                      "id_producto": precio.producto.id,
                      "datamsg": data_msg})

def form_crear_tipo_pago(request):
    data_msg = cargar_msg_session(request)
    return render(request, "tipo_pago/crear_tipo_pago.html",
                  {
                   "datamsg": data_msg})

def form_devoluciones_crear(request):
    data_msg = cargar_msg_session(request)
    return render(request, "devoluciones/crear-devolucion.html",
                  {
                   "datamsg": data_msg})

def crear_form_venta(request):
    data_msg = cargar_msg_session(request)
    return render(request, "ventas/crear-ventas.html",
                  {
                      "IP_SERVER": settings.IP_SERVER,
                   "datamsg": data_msg})

def crear_form_venta_contado(request):
    data_msg = cargar_msg_session(request)
    return render(request, "ventas/crear-venta-contado.html",
                  {
                      "IP_SERVER": settings.IP_SERVER,
                   "datamsg": data_msg})

def actualizar_venta_contado(request, id):
    venta = Venta.objects.all().get(id=id)
    data_msg = cargar_msg_session(request)
    """defaultValue": [
        {
            "textField": "1",
            "textField1": "3"
        },
        {
            "textField": "2",
            "textField1": "3"
        }
    ],"""
    detalles = DetalleVenta.objects.all().filter(venta=venta)
    values = []
    for d in detalles:
        obj = {}
        obj['id_detalle_venta'] = d.id
        obj['producto'] = d.producto.id
        obj['cantidad'] = d.cantidad
        obj['precio_unitario'] = d.precio_unitario
        obj['precioEspecial'] = d.precio_unitario
        if(d.is_precio_especial==True):
            obj['especial'] = 'true'
        else:
            obj['especial'] = 'false'
        obj['precioTotal'] = d.precio_total
        obj['estadoAutorizacion'] = d.estado_autorizacion.nombre
        if (d.is_precio_especial == True and d.estado_autorizacion.id==3):
            values.append(obj)
    return render(request, "ventas/actualizar_venta_contado.html",
                  {
                   "detalles": values,
                   "venta": venta,
                   "IP_SERVER": settings.IP_SERVER,
                   "datamsg": data_msg})


def ver_venta_para_concretar(request, id):
    venta = Venta.objects.all().get(id=id)
    data_msg = cargar_msg_session(request)
    """defaultValue": [
        {
            "textField": "1",
            "textField1": "3"
        },
        {
            "textField": "2",
            "textField1": "3"
        }
    ],"""
    detalles = DetalleVenta.objects.all().filter(venta=venta)
    values = []
    for d in detalles:
        obj = {}
        obj['id_detalle_venta'] = d.id
        obj['producto'] = d.producto.id
        obj['cantidad'] = d.cantidad
        obj['precio_unitario'] = d.precio_unitario
        obj['precioEspecial'] = d.precio_unitario
        if(d.is_precio_especial==True):
            obj['especial'] = 'true'
        else:
            obj['especial'] = 'false'
        obj['precioTotal'] = d.precio_total
        obj['estadoAutorizacion'] = d.estado_autorizacion.nombre

        values.append(obj)
    return render(request, "ventas/ver_venta_para_concretar.html",
                  {
                   "detalles": values,
                   "venta": venta,
                   "IP_SERVER": settings.IP_SERVER,
                   "datamsg": data_msg})

def form_crear_producto(request):
    data_msg = cargar_msg_session(request)
    return render(request, "producto/crear-producto.html",
                  {
                    "IP_SERVER": settings.IP_SERVER,
                   "datamsg": data_msg})

def form_crear_cliente(request):
    data_msg = cargar_msg_session(request)
    return render(request, "cliente/crear-cliente.html",
                  {
                   "datamsg": data_msg})