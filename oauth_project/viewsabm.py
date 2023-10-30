import json
import random
import string
import traceback
from datetime import datetime

from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from oauth_project.models.modelos import Proyecto, Estado, RolProyecto, Equipo, Integrante, Permiso, PermisoRol, \
    TipoUserStory, Miembro, UserStory, Sprint, Profile, RolUsuario, RolesSistema, Producto, Cliente, Venta, TipoVenta, \
    DetalleVenta, Devolucion, Categoria, TipoPago, PrecioProducto, EstadoAutorizacion, AutorizacionesRealizadas
from oauth_project.views import html

profile = Profile()


def crear_nuevo_usuario(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        user = request.POST['username']
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        error = ""
        if (password2 != password1):
            error = "Las contraseñas no coinciden\n"
        cant_users_name = User.objects.filter(username=user).count()
        if (cant_users_name > 0):
            error += "Ese nombre de usuario no se encuentra disponible"
        user_create = User(username=user, first_name=nombre, last_name=apellido, email=email,
                           password=make_password(password1))
        if (error == ""):
            user_create.save()
            # user_ = authenticate(request, username=user_create.username, password=password1)
            login(request, user_create, backend='django.contrib.auth.backends.ModelBackend')

            # login(request=request, user=user_, backend='django.contrib.auth.backends.ModelBackend')
            return html(request, 'home')
        else:
            context = {'error': error}
            return render(request, 'register.html', {'context': context})


@csrf_exempt
def crear_proyecto_post(request):
    # obtenemos el paquete data, con el json con los datos que necesitamos
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    print(data)
    proyect = Proyecto()
    # extraemos los datos necesarios, segun su key de formulario
    proyect.nombre_proyecto = data["nombre_proyecto"]
    proyect.descripcion = data["descripcion_proyecto"]
    id_scrum = get_id(data["scrum_master"])
    proyect.scrum_master = User.objects.all().get(id=id_scrum)
    # proyecto.fecha_inicio = ""
    # proyecto.fecha_fin = ""
    proyect.estado = Estado.objects.get(id=1)
    proyect.creado_by = request.user.id
    # armar json estados
    json_data_grid = data['datagrid_tipo_story']
    n = len(json_data_grid)
    list_tipos_storys = []
    for x in range(n):
        dic = {}
        object = json_data_grid[x]
        id = get_id(object['tipo_story-unique'])
        print('id estado a agregar es -> ' + str(id))
        tipo_user = TipoUserStory.objects.get(id=id)
        tipo_user.en_uso = True
        tipo_user.save()
        dic["id"] = tipo_user.id
        dic["nombre"] = tipo_user.descripcion
        dic["estados"] = tipo_user.estados
        list_tipos_storys.append(dic)
    print(list_tipos_storys)
    json_list_storys = json.dumps(list_tipos_storys)
    proyect.tipos_storys = json_list_storys
    proyect.save()
    print("El id del nuevo proyecto es --> " + str(proyect.id))
    # roles creados por defecto#
    rol = RolProyecto(descripcion='PRODUCTO OWNER', proyecto=proyect)
    rol.save()
    rol = RolProyecto(descripcion='TEAM LEAD', proyecto=proyect)
    rol.save()
    rol = RolProyecto(descripcion='DEVELOPER', proyecto=proyect)
    rol.save()
    equipo = Equipo()
    equipo.proyecto = proyect
    equipo.capacidad = 0
    equipo.save()
    msg = "El permiso " + str(proyect.id) + " - " + str(proyect.descripcion) + " fue creado éxitosamente"
    request.session["msg"] = msg
    return redirect("/proyectos")


@csrf_exempt
def crear_us_post(request):
    print('entra aca')
    # obtenemos el paquete data, con el json con los datos que necesitamos
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    print(data)
    user_story = UserStory()
    proyecto_id = get_id(data['proyecto_id'])
    tipo_story = TipoUserStory.objects.get(id=data['tipo_us'])
    user_story.proyecto = Proyecto.objects.get(id=proyecto_id)
    user_story.descripcion = data['descripcion_us']
    user_story.detalles = data['detalle_us']
    user_story.user_point = data['user_point']
    user_story.business_value = data['business_value']
    user_story.tipo_user_story = tipo_story
    user_story.estimacion_horas = data['estimacion_hora_us']
    user_story.estimacion_horas_inicial = data['estimacion_hora_us']
    user_story.eventos = "[]"
    user_story.estado = json.loads(tipo_story.estados)[0]
    user_story.agregar_evento(tipo_evento='sistema', descripcion='Creación de U.S', usuario=request.user.username,
                              data="")
    user_story.save()
    return redirect("/productbacklog/" + str(proyecto_id))


@csrf_exempt
def iniciar_proyecto_get(request, id):
    if not profile.verificar_permiso(request.user.id, id, 'iniciar-proyecto'):
        raise Http404
    print("llegó el id ->" + str(id))
    proyect = Proyecto.objects.get(id=id)
    proyect.estado = Estado.objects.get(id=2)
    proyect.fecha_inicio = datetime.now()
    proyect.save()
    msg = "El proyecto " + str(proyect.id) + " - " + str(proyect.descripcion) + " se ha iniciado éxitosamente"
    request.session["msg"] = msg
    return redirect("/proyectos")


@csrf_exempt
def iniciar_sprint_get(request, id, id_proyecto):
    print("INICIAR SPRINT:")
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'iniciar-sprint'):
        raise Http404

    all_user_story = UserStory.objects.all().values()
    for e in all_user_story:
        print(e['sprint_asoc_id'])
    print("Todos los User Story:" + str(all_user_story))
    user_story = UserStory.objects.filter(sprint_asoc=id)
    print("USER STORY: " + str(user_story))

    if not user_story:
        msg = "El sprint " + str(id) + "no tiene asociado ningun User Story"
        request.session["msg"] = msg
    else:
        print("llegó el id del sprint->" + str(id) + " id del proyecto->" + str(id_proyecto))
        sprint = Sprint.objects.get(id=id)
        sprint.estado = Estado.objects.get(id=2)
        sprint.fecha_inicio = datetime.now()
        sprint.save()
    return redirect("/sprints/" + str(id_proyecto))


@csrf_exempt
def finalizar_sprint_get(request, id, id_proyecto):
    print("---------------------Se impirme rquest de finalizar ")
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'finalizar-sprint'):
        raise Http404
    print("llegó el id del sprint->" + str(id) + " id del proyecto->" + str(id_proyecto))
    sprint = Sprint.objects.get(id=id)
    sprint.estado = Estado.objects.get(id=3)
    sprint.fecha_fin = datetime.now()
    datos = sprint.get_datos_informe()
    print('-----------------A JSON---------------------')
    print(datos)
    print('-----------------A JSON---------------------')
    sprint.json_informe_historico_finalizacion = json.dumps(sprint.get_datos_informe(), default=str)
    sprint.save()
    return redirect("/sprints/" + str(id_proyecto))


@csrf_exempt
def cancelar_sprint_get(request, id, id_proyecto):
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'cancelar-sprint'):
        raise Http404
    print("llegó el id del sprint->" + str(id) + " id del proyecto->" + str(id_proyecto))
    sprint = Sprint.objects.get(id=id)
    sprint.estado = Estado.objects.get(id=4)
    sprint.fecha_inicio = datetime.now()
    sprint.save()
    return redirect("/sprints/" + str(id_proyecto))


@csrf_exempt
def finalizar_proyecto_get(request, id):
    if not profile.verificar_permiso(request.user.id, id, 'finalizar-proyecto'):
        raise Http404
    proyect = Proyecto.objects.get(id=id)
    proyect.estado = Estado.objects.get(id=3)
    proyect.fecha_fin = datetime.now()
    proyect.save()
    msg = "El proyecto " + str(proyect.id) + " - " + str(proyect.descripcion) + " se ha finalizado éxitosamente"
    request.session["msg"] = msg
    return redirect("/proyectos")


@csrf_exempt
def cancelar_proyecto_get(request, id):
    if not profile.verificar_permiso(request.user.id, id, 'cancelar-proyecto'):
        raise Http404
    proyect = Proyecto.objects.get(id=id)
    proyect.estado = Estado.objects.get(id=4)
    proyect.fecha_fin = datetime.now()
    proyect.save()
    msg = "El proyecto " + str(proyect.id) + " - " + str(proyect.descripcion) + " se ha finalizado éxitosamente"
    request.session["msg"] = msg
    return redirect("/proyectos")


@csrf_exempt
def eliminar_permiso_delete(request, id):
    permiso = Permiso.objects.get(id=id)
    descripcion = permiso.descripcion
    permiso.delete()
    msg = "El permiso " + str(id) + " - " + str(descripcion) + " fue borrado"
    request.session["msg"] = msg
    return redirect("/permisos")


@csrf_exempt
def eliminar_tipo_story_get(request, id):
    tipo_story = TipoUserStory.objects.get(id=id).delete()
    msg = "El tipo de user story cod:" + str(id) + " fue eliminado"
    request.session["msg"] = msg
    return redirect("/tipos-user-story")


@csrf_exempt
def activar_devolucion_get(request, id):
    devolucion = Devolucion.objects.get(id=id)
    devolucion.is_active = True
    devolucion.save()
    msg = "La devolucion N°" + str(id) + " fue activado"
    request.session["msg"] = msg
    return redirect("/devoluciones")


@csrf_exempt
def desactivar_devolucion_get(request, id):
    devolucion = Devolucion.objects.get(id=id)
    devolucion.is_active = False
    devolucion.save()
    msg = "La devolucion N°" + str(id) + " fue desactivado"
    request.session["msg"] = msg
    return redirect("/devoluciones")


@csrf_exempt
def activar_usuario_get(request, id):
    user = User.objects.get(id=id)
    user.is_active = True
    user.save()
    msg = "El usuario N°" + str(id) + " fue activado"
    request.session["msg"] = msg
    return redirect("/usuarios")


@csrf_exempt
def desactivar_categoria_get(request, id):
    categoria = Categoria.objects.get(id=id)
    categoria.is_activo = False
    categoria.save()
    msg = "La categoria N°" + str(id) + " fue desactivada"
    request.session["msg"] = msg
    return redirect("/categorias")


@csrf_exempt
def desactivar_tipo_pago_get(request, id):
    tipo_pago = TipoPago.objects.get(id=id)
    tipo_pago.is_activo = False
    tipo_pago.save()
    msg = "El tipo de pago N°" + str(id) + " fue desactivada"
    request.session["msg"] = msg
    return redirect("/tipospagos")


@csrf_exempt
def eliminar_precio_get(request, id):
    precio = PrecioProducto.objects.get(id=id)
    id_producto = precio.producto.id
    precio.delete()
    msg = "El precio N°" + str(id) + " fue eliminado"
    request.session["msg"] = msg
    return redirect("/lista_precios/" + str(id_producto))


@csrf_exempt
def activar_tipo_pago_get(request, id):
    tipo_pago = TipoPago.objects.get(id=id)
    tipo_pago.is_activo = True
    tipo_pago.save()
    msg = "El tipo de pago N°" + str(id) + " fue activada"
    request.session["msg"] = msg
    return redirect("/tipospagos")


@csrf_exempt
def activar_categoria_get(request, id):
    categoria = Categoria.objects.get(id=id)
    categoria.is_activo = True
    categoria.save()
    msg = "La categoria N°" + str(id) + " fue activada"
    request.session["msg"] = msg
    return redirect("/categorias")


@csrf_exempt
def activar_producto_get(request, id):
    user = Producto.objects.get(id=id)
    user.is_active = True
    user.save()
    msg = "El producto N°" + str(id) + " fue activado"
    request.session["msg"] = msg
    return redirect("/productos")


@csrf_exempt
def desactivar_usuario_get(request, id):
    user = User.objects.get(id=id)
    user.is_active = False
    user.save()
    msg = "El usuario N°" + str(id) + " fue desactivado"
    request.session['msg'] = msg
    return redirect("/usuarios")


@csrf_exempt
def desactivar_producto_get(request, id):
    producto = Producto.objects.get(id=id)
    producto.is_active = False
    producto.save()
    msg = "El producto N°" + str(id) + " fue desactivado"
    request.session['msg'] = msg
    return redirect("/productos")


@csrf_exempt
def activar_cliente_get(request, id):
    cliente = Cliente.objects.get(id=id)
    cliente.is_active = True
    cliente.save()
    msg = "El cliente N°" + str(id) + " fue activado"
    request.session['msg'] = msg
    return redirect("/clientes")


@csrf_exempt
def autorizar_precio_get(request, id):
    detalle = DetalleVenta.objects.get(id=id)
    detalle.estado_autorizacion = EstadoAutorizacion.objects.get(id=2)
    detalle.save()
    autorizacion = AutorizacionesRealizadas.generar_autorizacion(detalle)
    autorizacion.fecha_autorizacion = datetime.now()
    autorizacion.usuario_autorizador = request.user
    autorizacion.save()
    msg = "El precio del detalle N°" + str(id) + " fue AUTORIZADO - APROBADO"
    request.session['msg'] = msg
    return redirect("/autorizaciones-pendientes")

@csrf_exempt
def desautorizar_precio_get(request, id):
    detalle = DetalleVenta.objects.get(id=id)
    detalle.estado_autorizacion = EstadoAutorizacion.objects.get(id=3)
    detalle.save()
    autorizacion = AutorizacionesRealizadas.generar_autorizacion(detalle)
    autorizacion.fecha_autorizacion = datetime.now()
    autorizacion.usuario_autorizador = request.user
    autorizacion.save()
    msg = "El precio del detalle N°" + str(id) + " fue DESAUTORIZADO - RECHAZADO"
    request.session['msg'] = msg
    return redirect("/autorizaciones-pendientes")

@csrf_exempt
def desactivar_cliente_get(request, id):
    cliente = Cliente.objects.get(id=id)
    cliente.is_active = False
    cliente.save()
    msg = "El cliente N°" + str(id) + " fue desactivado"
    request.session['msg'] = msg
    return redirect("/clientes")


@csrf_exempt
def reiniciar_password_get(request, id):
    user = User.objects.get(id=id)
    characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")
    length = 8
    random.shuffle(characters)
    password = []
    for i in range(length):
        password.append(random.choice(characters))
    random.shuffle(password)
    print('-------------------')
    new_password = "".join(password)
    print(new_password)
    print('-------------------')
    user.set_password(new_password)
    user.save()
    request.session[
        'msg'] = "Se ha reiniciado la contraseña de " + user.username + " Su nueva contraseña es -> [" + new_password + "]"
    return redirect("/usuarios")


@csrf_exempt
def modificar_equipo_proyecto_post(request):
    print('ESTE ES EL JSON ORIGINAL')
    post_data_json = request.POST['data']
    print('---conseguimos data---')
    print(post_data_json)
    print('---conseguimos data---')
    print('---pasamos a json---')
    json_object = json.loads(post_data_json)
    print(str(json_object))
    print('---pasamos a json---')
    print('---conseguimos proyecto id---')
    proyecto_id = get_id(json_object['proyecto_id'])
    print(str(proyecto_id))
    print(str(type(proyecto_id)))
    print('---conseguimos proyecto id---')
    n = len(json_object['dataGrid'])
    # eliminamos equipo anterior, creamos nuevo equipo
    equipo_ant = Equipo.objects.filter(proyecto=proyecto_id)
    equipo_ant.delete()
    # creamos nuevo equipo
    proyecto = Proyecto.objects.get(id=proyecto_id)
    equipo = Equipo()
    equipo.proyecto_id = proyecto.id
    equipo.capacidad = 0
    equipo.save()
    json_data_grid = json_object['dataGrid']

    for x in range(n):
        object = json_data_grid[x]
        integrante = Integrante()
        usuario_integrante = User.objects.get(id=object['integrante-unique'])
        print(str(usuario_integrante) + " tipo " + str(type(usuario_integrante)) + "  usuario_integrante: " + str(
            usuario_integrante.id) + " - " + str(usuario_integrante.username) + " tipo: " + str(
            type(object['integrante-unique'])) + " " + object['integrante-unique'])
        integrante.integrante_id = usuario_integrante.id
        integrante.cant_horas_dias = object['cant_horas']
        integrante.equipo_id = equipo.id
        integrante.save()
        print("---- se guardo un integrante ----")
        equipo.capacidad = equipo.capacidad + integrante.cant_horas_dias
    equipo.save()
    request.session['msg'] = "El equipo del proyecto N°: " + str(proyecto_id) + " fue actualizado exitosamente"
    return redirect('/proyectos')


@csrf_exempt
def crear_permiso_post(request):
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    permiso = Permiso()
    permiso.descripcion = data['descripcion_permiso']
    permiso.save()
    msg = "Se creó exitosamente el permiso N° " + str(permiso.id)
    request.session["msg"] = msg
    return redirect("/permisos")


@csrf_exempt
def crear_precio_producto_post(request, id):
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    precio = PrecioProducto()
    precio.producto = Producto.objects.get(id=data['id_producto'])
    precio.nombre = data['nombre']
    precio.precio = data['precio']
    try:
        precio.save()
        msg = "El nuevo precio es -> N° " + str(precio.id) + " - " + precio.nombre + " " + precio.precio
        request.session['msg'] = msg
    except:
        msg = "Ocurrió un error al crear el precio"
        request.session['msgerror'] = msg
    return redirect("/lista_precios/" + str(data['id_producto']))


@csrf_exempt
def modificar_precio_producto_post(request, id):
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    precio = PrecioProducto.objects.get(id=data['id_precio'])
    precio.producto = Producto.objects.get(id=data['id_producto'])
    precio.nombre = data['nombre']
    precio.precio = data['precio']
    try:
        precio.save()
        msg = "El precio actualizado es -> N° " + str(precio.id) + " - " + precio.nombre + " " + precio.precio
        request.session['msg'] = msg
    except:
        msg = "Ocurrió un error al crear el precio"
        request.session['msgerror'] = msg
        traceback.print_exc()
    return redirect("/lista_precios/" + str(data['id_producto']))


@csrf_exempt
def modificar_rol_post(request, id, id_proyecto_id):
    rol = RolProyecto.objects.get(id=id)
    print(rol)
    desc = request.POST.get('data[descripcion_rol]')
    print("nuevo rol -> " + desc)
    rol.descripcion = desc
    rol.save()
    rolesporporyecto = RolProyecto.objects.all().filter(proyecto=id_proyecto_id)
    return render(request, "roles-proyecto.html",
                  {"rolesporproyecto": rolesporporyecto, "id_proyecto_id": id_proyecto_id})


@csrf_exempt
def actualizar_permisos_rol_post(request):
    print(request.POST)
    post_data_json = request.POST['data']
    json_object = json.loads(post_data_json)
    rol_id = json_object['idRol']
    rol = RolProyecto.objects.get(id=rol_id)
    json_permisos = json_object['permisos']
    for p in json_permisos:
        habilitado = json_permisos[p]
        cod_permiso = p
        if habilitado:
            p_rol = PermisoRol()
            p_rol.permiso = Permiso.objects.get(id=cod_permiso)
            p_rol.rol = rol
            obj, created = PermisoRol.objects.get_or_create(
                permiso_id=p,
                rol_id=rol_id,
            )
        if not habilitado:
            PermisoRol.objects.filter(permiso_id=cod_permiso, rol_id=rol_id).delete()
    request.session['msg'] = "Se actualizó los permisos de " + str(rol.descripcion) + " exitosamente"
    return redirect('/roles-proyecto/' + str(rol.proyecto.id))
    # return render(request, "roles-proyecto.html")


@csrf_exempt
def crear_tipo_user_story(request):
    # obtenemos el paquete data, con el json con los datos que necesitamos
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(normalize(post_data_json))
    tipo_story = TipoUserStory()
    tipo_story.descripcion = data["nombre_tipo_story"]
    # extraemos los datos necesarios, segun su key de formulario
    aux_estados = data["dataGrid"]
    n = len(aux_estados)
    estados = []
    for x in range(n):
        estados.append(aux_estados[x]['estado-unique'])
    tipo_story.estados = json.dumps(estados)
    tipo_story.save()
    request.session["msg"] = "El id del nuevo Tipo de Story es --> " + str(tipo_story.id)
    return redirect("/tipos-user-story")


@csrf_exempt
def view_agregar_sprint_proyecto(request):
    # obtenemos el paquete data, con el json con los datos que necesitamos
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(normalize(post_data_json))
    id_proyecto = data["id_proyecto"]
    integrantes = Integrante.objects.filter(equipo__proyecto__id=id_proyecto).select_related("integrante")
    print('------------------- Integrantes por defecto del Sprint')
    print(integrantes)
    print('-------------------')
    equipo = []
    cant_horas_total = 0

    for x in integrantes:
        dic = {}
        miembro = Miembro.objects.filter(user_id=x.integrante_id)[0]
        # dic["id"] = miembro.user.id
        dic["id"] = x.integrante.id
        dic["nombre"] = x.integrante.username
        dic["cant_horas"] = x.cant_horas_dias
        cant_horas_total = cant_horas_total + x.cant_horas_dias
        equipo.append(dic)
    print("-----------------KLa cantidad total de horas es " + str(cant_horas_total))
    equipo_cap = Equipo.objects.get(proyecto_id=id_proyecto)
    print("El equipo del proyecto " + str(id_proyecto) + " tiene id " + str(equipo_cap.id) + "  " + str(equipo_cap))
    equipo_cap.capacidad = cant_horas_total
    equipo_cap.save()
    integrantes_json = json.dumps(equipo)
    print('------------------- Integrantes en formato json')
    print(integrantes_json)
    print('-------------------')
    proyecto = Proyecto.objects.get(id=id_proyecto)
    nro_sprint = data["nro_sprint"]
    descripcion_sprint = data["descripcion_sprint"]
    duracion_sprint = data["duracion_sprint"]
    objetivos = data["objetivos"]
    tipos_us = proyecto.tipos_storys
    sprint = Sprint()
    sprint.proyecto = proyecto
    sprint.nro_sprint = nro_sprint
    sprint.descripcion = descripcion_sprint
    sprint.cant_dias_duracion = duracion_sprint
    sprint.objetivo = objetivos
    sprint.tipos_storys = tipos_us
    sprint.equipo = integrantes_json
    sprint.estado = Estado.objects.get(id=1)
    sprint.carga_horas_diarias_equipo = cant_horas_total
    sprint.save()
    request.session["msg"] = "El id del nuevo Sprint de Story es --> " + str(sprint.id)
    return redirect("/sprints/" + str(proyecto.id))


@csrf_exempt
def view_modificar_sprint_proyecto(request):
    """
               Metodo view_modificar_sprint_proyecto::

                               def view_modificar_sprint_proyecto(request):

                Metodo para modificar un sprint con estado Creado, se puede
                modificar la descipcion y los objetivos del sprint

                       A través del parámetro recibido *request* obtenidos por POST,
                obtiene los datos del formulario en formato json, del obtiene el id del sprint,
                id del proyecto y los nuevos campos de descripcion y objetivos, a traves de la clave
                del label del form

                    Se instancia un nuevo Sprint y se asignan lso valores para ser actualizado

                    Se guarda en la base de datos

                       Args:

                           request: Es un objeto de solicitud que recibe
                       Returns:

                               Redirect con redireccion a sprints con el id del proyecto
   """
    # obtenemos el paquete data, con el json con los datos que necesitamos
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(normalize(post_data_json))
    id_sprint = data["nro_sprint"]
    sprint = Sprint.objects.get(id=id_sprint)
    new_descripcion = data['descripcion_sprint']
    new_objetivo = data['objetivos']
    id_proyecto = data['proyecto']
    print("descripcion y objetivo")
    print(str(new_descripcion))
    print(str(new_objetivo))
    sprint.descripcion = new_descripcion
    sprint.objetivo = new_objetivo
    sprint.save()
    return redirect("/sprints/" + str(id_proyecto))


@csrf_exempt
def actualizar_tipo_user_story_pos(request):
    # obtenemos el paquete data, con el json con los datos que necesitamos
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    id = get_id(data["id_tipo_story"])
    tipo_story = TipoUserStory.objects.get(id=id)
    tipo_story.descripcion = data["nombre_tipo_story"]
    # extraemos los datos necesarios, segun su key de formulario
    aux_estados = data["dataGrid"]
    n = len(aux_estados)
    estados = []
    for x in range(n):
        estados.append(aux_estados[x]['estado-unique'])
    tipo_story.estados = json.dumps(estados)
    tipo_story.save()
    request.session["msg"] = "El Tipo de User Story --> " + str(tipo_story.id) + " se ha actualizado correctamente"
    return redirect("/tipos-user-story")


@csrf_exempt
def registrar_evento_us(request):
    # obtenemos el paquete data, con el json con los datos que necesitamos
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    horas = 0
    if (data['horas'] != ''):
        horas = get_id(data['horas'])
    if (horas == 0):
        id_us = get_id(data['id_user_story'])
        observacion = data['detalle_evento']
        user_story = UserStory.objects.get(id=id_us)
        user_story.agregar_evento(tipo_evento='observacion', descripcion=observacion, usuario=request.user.username,
                                  data="")
        # extraemos los datos necesarios, segun su key de formulario
        user_story.save()
        request.session["msg"] = "El User Story --> " + str(id_us) + " se ha actualizado correctamente"
    else:
        id_us = get_id(data['id_user_story'])
        observacion = data['detalle_evento']
        data = {}
        data['user_horas'] = request.user.username
        data['cant_horas'] = horas
        user_story = UserStory.objects.get(id=id_us)
        user_story.agregar_evento(tipo_evento='registro_horas', descripcion=observacion, usuario=request.user.username,
                                  data=data)
        # extraemos los datos necesarios, segun su key de formulario
        user_story.save()
        request.session["msg"] = "El User Story --> " + str(id_us) + " se ha actualizado correctamente"

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@csrf_exempt
def registrar_evento_us_kanban(request):
    # obtenemos el paquete data, con el json con los datos que necesitamos
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    us_story = UserStory.objects.get(id=get_id(data['id_user_story']))

    horas = 0
    if (data['horas'] != ''):
        horas = get_id(data['horas'])
    if (horas == 0):
        id_us = get_id(data['id_user_story'])
        observacion = data['detalle_evento']
        user_story = UserStory.objects.get(id=id_us)
        user_story.agregar_evento(tipo_evento='observacion', descripcion=observacion, usuario=request.user.username,
                                  data="")
        # extraemos los datos necesarios, segun su key de formulario
        user_story.save()
        request.session["msg"] = "El User Story --> " + str(id_us) + " se ha actualizado correctamente"
    else:
        id_us = get_id(data['id_user_story'])
        observacion = data['detalle_evento']
        data = {}
        data['user_horas'] = request.user.username
        data['cant_horas'] = horas
        user_story = UserStory.objects.get(id=id_us)
        data['sprint_id'] = user_story.sprint_asoc.id
        user_story.agregar_evento(tipo_evento='registro_horas', descripcion=observacion, usuario=request.user.username,
                                  data=data)
        # extraemos los datos necesarios, segun su key de formulario
        user_story.save()
        request.session["msg"] = "El User Story --> " + str(id_us) + " se ha actualizado correctamente"
    # return redirect('ver-tablero/'+str(us_story.sprint_asoc)+'/'+str(us<int:nro_tipo_user>')
    return redirect('/ver-tablero/' + str(us_story.sprint_asoc.id) + '/' + str(us_story.nro_tipo_us()))


@csrf_exempt
def crear_rol_post(request):
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    id_proyecto = data['id_proyecto']
    print("EL ID DEL PROYECTO ES ----> " + str(id_proyecto))
    print(request.POST)
    rolporproyecto = RolProyecto()
    proyecto = Proyecto.objects.get(id=id_proyecto)
    rolporproyecto.descripcion = data['descripcion_rol']
    rolporproyecto.proyecto = proyecto
    print(rolporproyecto)
    rolporproyecto.save()
    rolesporporyecto = RolProyecto.objects.all().filter(proyecto=id_proyecto)
    print("El id del nuevo rol es --> " + str(rolporproyecto.id))
    msg = "El id del nuevo rol es --> " + str(rolporproyecto.id)
    request.session["msg"] = msg
    return render(request, "roles-proyecto.html",
                  {"rolesporproyecto": rolesporporyecto, "id_proyecto_id": id_proyecto})


@csrf_exempt
def crear_rol_post(request):
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    print(request.POST)
    rol_sistema_nuevo = RolesSistema()
    rol_sistema_nuevo.descripcion = data['descripcion_rol']
    print(rol_sistema_nuevo)
    rol_sistema_nuevo.save()
    print("El nuevo rol es --> N° " + str(rol_sistema_nuevo.id) + " - " + str(rol_sistema_nuevo.descripcion))
    msg = "El nuevo rol es --> N° " + str(rol_sistema_nuevo.id) + " - " + str(rol_sistema_nuevo.descripcion)
    request.session["msg"] = msg
    return (redirect("/roles-sistema"))


@csrf_exempt
def crear_usuario_sistema_post(request):
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    print(request.POST)
    user = User()
    user.is_active = True
    user.is_staff = False
    user.is_superuser = False
    user.email = data['correo']
    user.username = data['username']
    user.last_name = data['apellido']
    user.first_name = data['nombre']
    try:
        user.save()
        msg = "El nuevo usuario es -> N° " + str(user.id) + " - " + user.first_name + " " + user.last_name
        request.session['msg'] = msg
    except:
        msg = "Ocurrió un error al crear el usuario"
        request.session['msgerror'] = msg
    request.session["msg"] = msg
    return redirect("/usuarios")


def crear_usuario_sistema_post(request):
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    print(request.POST)
    user = User()
    user.is_active = True
    user.is_staff = False
    user.is_superuser = False
    user.email = data['correo']
    user.username = data['username']
    user.last_name = data['apellido']
    user.first_name = data['nombre']
    try:
        user.save()
        msg = "El nuevo usuario es -> N° " + str(user.id) + " - " + user.first_name + " " + user.last_name
        request.session['msg'] = msg
    except:
        msg = "Ocurrió un error al crear el usuario"
        request.session['msgerror'] = msg
    request.session["msg"] = msg
    return redirect("/usuarios")


@csrf_exempt
def crear_categoria_sistema_post(request):
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    print(request.POST)
    categoria = Categoria()
    categoria.is_activo = True
    categoria.nombre = data['nombre']
    try:
        categoria.save()
        msg = "La nueva categoría es -> N° " + str(categoria.id) + " - " + categoria.nombre
        request.session['msg'] = msg
    except:
        msg = "Ocurrió un error al crear la categoria"
        request.session['msgerror'] = msg
    request.session["msg"] = msg
    return redirect("/categorias")


@csrf_exempt
def crear_tipo_pago_sistema_post(request):
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    print(request.POST)
    tipo_pago = TipoPago()
    tipo_pago.is_activo = True
    tipo_pago.nombre = data['nombre']
    try:
        tipo_pago.save()
        msg = "El nuevo tipo pago es -> N° " + str(tipo_pago.id) + " - " + tipo_pago.nombre
        request.session['msg'] = msg
    except:
        msg = "Ocurrió un error al crear el tipo de pago"
        request.session['msgerror'] = msg
    request.session["msg"] = msg
    return redirect("/tipospagos")


@csrf_exempt
def actualizar_tipo_pago_sistema_post(request):
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    print(request.POST)
    tipo_pago = TipoPago.objects.get(id=data['id'])
    tipo_pago.is_activo = True
    tipo_pago.nombre = data['nombre']
    try:
        tipo_pago.save()
        msg = "El nuevo tipo pago es -> N° " + str(tipo_pago.id) + " - " + tipo_pago.nombre
        request.session['msg'] = msg
    except:
        msg = "Ocurrió un error al crear el tipo pago"
        request.session['msgerror'] = msg
    request.session["msg"] = msg
    return redirect("/tipospagos")


@csrf_exempt
def crear_categoria_sistema_post(request):
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    print(request.POST)
    categoria = Categoria()
    categoria.is_activo = True
    categoria.nombre = data['nombre']
    try:
        categoria.save()
        msg = "La nueva categoría es -> N° " + str(categoria.id) + " - " + categoria.nombre
        request.session['msg'] = msg
    except:
        msg = "Ocurrió un error al crear la categoria"
        request.session['msgerror'] = msg
    request.session["msg"] = msg
    return redirect("/categorias")


@csrf_exempt
def actualizar_categoria_sistema_post(request):
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    print(request.POST)
    categoria = Categoria.objects.get(id=data['id'])
    categoria.is_activo = True
    categoria.nombre = data['nombre']
    try:
        categoria.save()
        msg = "La nueva categoría es -> N° " + str(categoria.id) + " - " + categoria.nombre
        request.session['msg'] = msg
    except:
        msg = "Ocurrió un error al crear la categoria"
        request.session['msgerror'] = msg
    request.session["msg"] = msg
    return redirect("/categorias")


@csrf_exempt
def crear_devolucion_post(request):
    print('PROCESO DE VENTA')
    post_data_json = request.POST['data']
    data = json.loads(post_data_json)
    print(request.POST)
    devolucion = Devolucion()
    devolucion.motivo_devolucion = data['motivo']
    devolucion.fecha_devolucion = datetime.now()
    devolucion.is_activo = True
    devolucion.producto = Producto.objects.get(id=data['producto']['id'])
    venta = Venta.objects.get(id=data['pedido'])
    devolucion.cliente = venta.cliente
    devolucion.cantidad = data['cantidad']
    devolucion.venta = venta
    devolucion.monto_devolucion = data['total_devolver']
    try:
        devolucion.save()
        msg = "La nueva devolucion -> N° " + str(devolucion.id)
        request.session['msg'] = msg
    except Exception as e:
        msg = "Ocurrió un error al crear la devolucion: " + str(e)
        request.session['msgerror'] = msg
        print(msg)  # Imprime el error en la consola
        traceback.print_exc()
    return redirect("/devoluciones")


@csrf_exempt
def crear_venta_contado_post(request):
    estado = "PENDIENTE DE PROCESO"
    post_data_json = request.POST['data']
    data = json.loads(post_data_json)
    print(request.POST)
    venta = Venta()
    venta.tipo_venta = TipoVenta.objects.get(id=1)
    venta.cliente = Cliente.objects.get(id=data['cliente'])
    fecha_venta = datetime.now()
    venta.fecha_venta = fecha_venta
    detalles = data['detalles_venta']
    print('detalles_ventas')
    print(detalles)
    venta.cantidad_articulos = len(detalles)
    venta.monto_total = data['total']
    venta.pagado = False
    venta.vendedor = User.objects.filter(username=request.user)[0]
    estado_precio_normal = EstadoAutorizacion.objects.get(id=4)
    estado_pendiente = EstadoAutorizacion.objects.get(id=1)
    precio_especial = False
    for d in detalles:
        print("detalle: ->>>")
        print(d)
        if (d['especial'] == True):
            precio_especial = True
            break
    if (precio_especial):
        estado = "ESPERA DE APROBACION PRECIO ESPECIAL"
    detalle_venta = []
    for d in detalles:
        detalle = DetalleVenta()
        detalle.producto = Producto.objects.get(id=d['producto'])
        detalle.cantidad = d['cantidad']
        if d['especial'] == True:
            detalle.precio_unitario = d['precioEspecial']
            detalle.estado_autorizacion = estado_pendiente
        else:
            detalle.precio_unitario = d['precio_unitario']
            detalle.estado_autorizacion = estado_precio_normal
        detalle.is_precio_especial = d['especial']
        detalle.precio_total = d['precioTotal']
        print(detalle_venta)
        detalle_venta.append(detalle)
    venta.estado = Estado.objects.filter(descripcion=estado)[0]
    try:
        venta.save()
        print("Se creo la venta y se van a crear N Detalles ->" + str(len(detalle_venta)))
        for d in detalle_venta:
            d.venta = venta
            d.save()
        msg = "La nueva venta -> N° " + str(venta.id) + " con " + str(len(detalle_venta)) + " detalles"
        request.session['msg'] = msg
    except Exception as e:
        msg = "Ocurrió un error al crear la venta: " + str(e)
        request.session['msgerror'] = msg
        print(msg)  # Imprime el error en la consola
        traceback.print_exc()
    return redirect("/ventas")


@csrf_exempt
def actualizar_venta_contado_post(request):
    try:
        post_data_json = request.POST['data']
        data = json.loads(post_data_json)
        print(request.POST)
        detalles = data['detalles_venta']
        precio_especial = False
        for d in detalles:
            if (d['especial'] == True):
                precio_especial = True
                break
        for d in detalles:
            detalle = DetalleVenta.objects.get(id=d['id_detalle_venta'])
            if d['especial'] == True or d['especial'] == 'true':
                detalle.precio_unitario = d['precioEspecial']
                detalle.estado_autorizacion = EstadoAutorizacion.objects.get(id=1)
            detalle.precio_total = d['precioTotal']
            detalle.save()
        msg = "Se actualizaron detalles de venta"
        request.session['msg'] = msg
    except Exception as e:
        msg = "Ocurrió un error al actualizar la venta: " + str(e)
        request.session['msgerror'] = msg
        print(msg)  # Imprime el error en la consola
        traceback.print_exc()

    return redirect("/ventas-pendientes-modificacion")

@csrf_exempt
def crear_venta_post(request):
    print('PROCESO DE VENTA')
    estado = "PENDIENTE DE PROCESO"
    post_data_json = request.POST['data']
    data = json.loads(post_data_json)
    print(request.POST)
    venta = Venta()
    venta.tipo_venta = TipoVenta.objects.get(id=data['tipo_venta'])
    venta.cliente = Cliente.objects.get(id=data['cliente'])
    fecha_venta = datetime.now()
    venta.fecha_venta = fecha_venta
    detalles = data['detalles_venta']
    print('detalles_ventas')
    print(detalles)
    venta.cantidad_articulos = len(detalles)
    venta.monto_total = data['total']
    venta.pagado = False
    venta.vendedor = User.objects.filter(username=request.user)[0]

    precio_especial = False
    for d in detalles:
        print("detalle: ->>>")
        print(d)
        if (d['especial'] == True):
            precio_especial = True
            break
    if (precio_especial):
        estado = "ESPERA DE APROBACION PRECIO ESPECIAL"
    detalle_venta = []
    for d in detalles:
        detalle = DetalleVenta()
        detalle.producto = Producto.objects.get(id=d['producto'])
        detalle.cantidad = d['cantidad']
        if d['especial'] == True:
            detalle.precio_unitario = d['precioEspecial']
        else:
            detalle.precio_unitario = d['precio_unitario']
        detalle.is_precio_especial = d['especial']
        detalle.precio_total = d['precioTotal']
        print(detalle_venta)
        detalle_venta.append(detalle)
    venta.estado = Estado.objects.filter(descripcion=estado)[0]
    try:
        venta.save()
        print("Se creo la venta y se van a crear N Detalles ->" + str(len(detalle_venta)))
        for d in detalle_venta:
            d.venta = venta
            d.save()
        msg = "La nueva venta -> N° " + str(venta.id) + " con " + str(len(detalle_venta)) + " detalles"
        request.session['msg'] = msg
    except Exception as e:
        msg = "Ocurrió un error al crear la venta: " + str(e)
        request.session['msgerror'] = msg
        print(msg)  # Imprime el error en la consola
        traceback.print_exc()
    return redirect("/ventas")


@csrf_exempt
def crear_producto_post(request):
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    print(request.POST)
    producto = Producto()
    producto.descripcion = data['nombre']
    producto.categoria = Categoria.objects.get(id=data['id_categoria'])
    producto.cantidad_stock = data['cantidad_stock_inicial']
    producto.is_active = True
    try:
        producto.save()
        msg = "El nuevo producto es -> N° " + str(producto.id) + " - " + producto.descripcion
        request.session['msg'] = msg
    except:
        msg = "Ocurrió un error al crear el producto"
        request.session['msgerror'] = msg
    request.session["msg"] = msg
    return redirect("/productos")


@csrf_exempt
def crear_cliente_post(request):
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    print(request.POST)
    cliente = Cliente()
    cliente.nombre = data['nombre']
    cliente.telefono = data['telefono']
    cliente.documento = data['documento']
    cliente.is_active = True
    try:
        cliente.save()
        msg = "El nuevo cliente es -> N° " + str(cliente.id) + " - " + cliente.nombre
        request.session['msg'] = msg
    except:
        msg = "Ocurrió un error al crear el cliente"
        request.session['msgerror'] = msg
    request.session["msg"] = msg
    return redirect("/clientes")


@csrf_exempt
def modificar_cliente_post(request, id):
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    print(request.POST)
    cliente = Cliente.objects.get(id=id)
    cliente.nombre = data['nombre']
    cliente.telefono = data['telefono']
    cliente.documento = data['documento']
    try:
        cliente.save()
        msg = "El cliente actualizado es -> N° " + str(cliente.id) + " - " + cliente.nombre
        request.session['msg'] = msg
    except:
        msg = "Ocurrió un error al modificar el cliente"
        request.session['msgerror'] = msg
    request.session["msg"] = msg
    return redirect("/clientes")


@csrf_exempt
def modificar_producto_post(request, id):
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    print(request.POST)
    producto = Producto.objects.get(id=id)
    producto.descripcion = data['nombre']
    producto.cantidad_stock = data['cantidad_stock']
    try:
        producto.save()
        msg = "El producto actualizado es -> N° " + str(producto.id) + " - " + producto.descripcion
        request.session['msg'] = msg
    except:
        msg = "Ocurrió un error al modificar el producto"
        request.session['msgerror'] = msg
    request.session["msg"] = msg
    return redirect("/productos")


@csrf_exempt
def actualizar_rol_usuario(request, id_usuario):
    print("EL ID DEL usuario  ES ----> " + str(id_usuario))
    print(request.POST)
    post_data_json = request.POST['data']
    json_object = json.loads(post_data_json)
    print("------------------------$$$$$$$$$")
    print(str(json_object))
    roles = json_object['roles']
    print(roles)
    # Obtén el usuario
    user = User.objects.get(id=id_usuario)

    # Filtra todos los objetos RolUsuario relacionados con el usuario
    roles_usuario = RolUsuario.objects.filter(usuario=user)

    # Elimina todos los objetos RolUsuario relacionados con el usuario
    roles_usuario.delete()
    for r in roles:
        r1 = RolUsuario()
        rol_sistema = RolesSistema()
        rol_sistema.id = r
        r1.rol = rol_sistema
        r1.usuario = user
        r1.save()
    request.session["msg"] = "Los roles del usuario fueron actualizados "
    return redirect('/usuarios')
    """"
    print("El rol a importar es -> " + str(id_rol))
    print(str(type(id_rol)))

    descripRolProyecto = RolProyecto.objects.get(id=id_rol)
    print("descripcionRolProyecto: "+str(descripRolProyecto.descripcion))
    rolporproyecto = RolProyecto()
    proyecto = Proyecto.objects.get(id=id_proyecto_id)
    print("proyecto "+str(proyecto.id)+str(proyecto.descripcion))
    rolporproyecto.descripcion = descripRolProyecto.descripcion
    rolporproyecto.proyecto = proyecto
    print("Rol por proyecto")
    rolporproyecto.save()
    print(rolporproyecto)

    permisosRol = PermisoRol.objects.filter(rol_id=id_rol)
    print(permisosRol)
    for p in permisosRol:
            print("permiso id: "+str(p.id))
            p_rol = PermisoRol()
            p_rol.permiso = Permiso.objects.get(id=p.permiso.id)
            p_rol.rol = rolporproyecto
            p_rol.save()

    rolesporporyecto = RolProyecto.objects.all().filter(proyecto=id_proyecto_id)
    request.session["msg"] = "El id del rol a importar es --> " + str(rolporproyecto.id)
    return render(request, "roles-proyecto.html", {"id_proyecto_id": id_proyecto_id, "rolesporproyecto": rolesporporyecto})
    """


@csrf_exempt
def importar_rol_post(request, id_proyecto_id):
    print("EL ID DEL PROYECTO ES ----> " + str(id_proyecto_id))
    print(request.POST)
    post_data_json = request.POST['data']
    json_object = json.loads(post_data_json)
    print("------------------------$$$$$$$$$")
    print(str(json_object))
    id_rol = json_object['rol']
    print("El rol a importar es -> " + str(id_rol))
    print(str(type(id_rol)))

    descripRolProyecto = RolProyecto.objects.get(id=id_rol)
    print("descripcionRolProyecto: " + str(descripRolProyecto.descripcion))
    rolporproyecto = RolProyecto()
    proyecto = Proyecto.objects.get(id=id_proyecto_id)
    print("proyecto " + str(proyecto.id) + str(proyecto.descripcion))
    rolporproyecto.descripcion = descripRolProyecto.descripcion
    rolporproyecto.proyecto = proyecto
    print("Rol por proyecto")
    rolporproyecto.save()
    print(rolporproyecto)

    permisosRol = PermisoRol.objects.filter(rol_id=id_rol)
    print(permisosRol)
    for p in permisosRol:
        print("permiso id: " + str(p.id))
        p_rol = PermisoRol()
        p_rol.permiso = Permiso.objects.get(id=p.permiso.id)
        p_rol.rol = rolporproyecto
        p_rol.save()

    rolesporporyecto = RolProyecto.objects.all().filter(proyecto=id_proyecto_id)
    request.session["msg"] = "El id del rol a importar es --> " + str(rolporproyecto.id)
    return render(request, "roles-proyecto.html",
                  {"id_proyecto_id": id_proyecto_id, "rolesporproyecto": rolesporporyecto})


@csrf_exempt
def modificar_rol_post(request, id, id_proyecto_id):
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)

    rol = RolProyecto.objects.get(id=id)
    print(rol)
    desc = data['descripcion_rol']
    print("nuevo rol -> " + desc)
    rol.descripcion = desc
    rol.save()
    rolesporporyecto = RolProyecto.objects.all().filter(proyecto=id_proyecto_id)
    return render(request, "roles-proyecto.html",
                  {"rolesporproyecto": rolesporporyecto, "id_proyecto_id": id_proyecto_id})


def get_id(id):
    return str(id).replace("'", '')


def normalize(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s


@csrf_exempt
def agregar_integrante_proyecto_post(request, id_proyecto):
    print(request.POST)
    # recibe por post, el id del miembro y la cantidad de horas
    post_data_json = request.POST['data']
    json_object = json.loads(post_data_json)
    id_miembro = json_object['miembro']
    cant_horas = json_object['horas']
    print("El id del miembro->" + str(id_miembro) + " la cantidad de horas->" + str(cant_horas))
    miembro = Miembro.objects.get(id=id_miembro)
    print("el miembro es ---------------------> " + str(miembro))
    user = User.objects.get(id=miembro.user.id)
    print("el user es ---------------------> " + str(user.id))
    equipo = Equipo.objects.all().filter(proyecto_id=id_proyecto)
    print("el equipo del proyecto " + str(id_proyecto) + " es " + str(equipo[0]))
    integrante = Integrante()
    integrante.integrante = user
    integrante.cant_horas_dias = cant_horas
    integrante.equipo = equipo[0]
    integrante.save()
    print("el id del miembro a agregar a integrantes es: " + str(id_miembro))
    return redirect('/proyectos-integrantes/' + str(id_proyecto))
    # return render(request, "roles-proyecto.html")


@csrf_exempt
def agregar_miembro_proyecto_post(request, id_proyecto):
    """
                   Metodo agregar_miembro_proyecto_post::

                           def agregar_miembro_proyecto_post(request, id_proyecto):

                   Metodo para agregar un miembro de un proyecto

                   A través del parámetro recibido *request* obtenidos por POST,
            obtiene los datos del formulario en formato json, del obtiene el id del rol a traves de la clave
            del label del form, ademas obtiene el id del miembro

                Se instancia un nuevo Miembro y se asigna los nuevo valores al nuevo miembro

                Se guarda en la base de datos

                   Se genera un mensaje de realizacion y se envia a traves de *request.SESSION*

                   Args:

                       request: Es un objeto de solicitud que recibe
                       id_proyecto (int): El identificador del proyecto que recibe
                   Returns:

                           Redirect con redireccion a proyectos-miembros
    """
    print(request.POST)
    post_data_json = request.POST['data']
    json_object = json.loads(post_data_json)
    id_miembro = json_object['miembro']
    print("EL nuevo usuario como miembro es " + str(id_miembro))
    id_rol = json_object['rol']
    miembros = Miembro.objects.filter(rol__proyecto_id=id_proyecto)
    print("-----miembros------")
    print(miembros)
    print("-----miembros------")
    duplicado = False
    print(" type id_miembro: " + str(type(id_miembro)))
    print("type id_rol: " + str(type(id_rol)))
    print("id_miembro: " + str(id_miembro))
    print("id_rol: " + str(id_rol))
    for i in miembros:
        print("user_id: " + str(i.user_id) + " id_miembro: " + str(id_miembro) + " rol_id: " + str(
            i.rol_id) + " id_rol: " + str(id_rol))
        if (i.user_id == int(id_miembro)) and (i.rol_id == id_rol):
            duplicado = True
    print("duplicado: " + str(duplicado))
    if duplicado:
        msg = "No se puede agregar un miembro existente con el mismo rol"
        print(msg)
        request.session['msgerror'] = msg
    else:
        nuevo_miembro = Miembro()
        nuevo_miembro.rol_id = id_rol
        nuevo_miembro.user_id = id_miembro
        nuevo_miembro.save()
        msg = "Se creo el nuevo miembro con id -> " + str(id_miembro) + " exitosamente"
        request.session['msg'] = msg

    return redirect('/proyectos-miembros/' + str(id_proyecto))
    # return render(request, "roles-proyecto.html")


@csrf_exempt
def eliminar_miembro_proyecto_delete(request, id_miembro, id_proyecto):
    if not profile.verificar_permiso(request.user.id, id_proyecto, 'eliminar-miembro'):
        raise Http404

    """
               Metodo eliminar_miembro_proyecto_delete::

                       def eliminar_miembro_proyecto_delete(request, id_miembro, id_proyecto):

               Metodo para eliminar un miembro de un proyecto

               Se obtiene el miembro a elimianr con el parametro recibido *id_miembro*

               Se elimina de la base de datos

               Se genera un mensaje de realizacion y se envia a traves de *request.SESSION*

               Args:
               
                   request: Es un objeto de solicitud que recibe
                   id_miembro (int): El identificador del miembro que recibe
                   id_proyecto (int): El identificador del proyecto que recibe
               Returns:
               
                       Redirect con redireccion a proyectos-miembros
    """
    miembro = Miembro.objects.get(id=id_miembro)
    miembro.delete()
    msg = "El miembro con id -> " + str(id_miembro) + " fue borrado del proyecto con id -> " + str(id_proyecto)
    request.session["msg"] = msg
    return redirect('/proyectos-miembros/' + str(id_proyecto))


@csrf_exempt
def modificar_miembro_proyecto_post(request, id_miembro, id_proyecto):
    """
            Metodo modificar_miembro_proyecto_post::

                    def modificar_miembro_proyecto_post(request, id_miembro, id_proyecto):

            Metodo para modificar un miembro al un proyecto

            A través del parámetro recibido *request* obtenidos por POST,
            obtiene los datos del formulario en formato json, del obtiene el id del rol a traves de la clave
            del label del form, ademas obtiene el id del miembro

            Se verifica si el rol anterior no coincide con el nuevo rol a asignar el miembro, el caso de que no
            coincida se realiza la actualizacion y en caso contrario se envia un mesaje de error.

            Args:

                request: Es un objeto de solicitud que recibe
                id_miembro (int): El identificador del miembro que recibe
                id_proyecto (int): El identificador del proyecto que recibe
            Returns:

                    Redirect con redireccion a proyectos-miembros
    """
    print(request.POST)
    post_data_json = request.POST['data']
    json_object = json.loads(post_data_json)
    id_miembro = json_object['miembro']
    print("EL usuario a modificar es " + str(id_miembro))
    id_rol = json_object['rol']
    anterior_miembro = Miembro.objects.get(id=id_miembro)
    if (anterior_miembro.rol_id == id_rol):
        msg = "No se pudo modificar a un rol ya asignado"
        request.session['msg'] = msg
    else:
        miembro_modificado = Miembro.objects.get(id=id_miembro)
        miembro_modificado.rol_id = id_rol
        miembro_modificado.save()
        request.session['msg'] = "Se modifico el miembro con id -> " + str(id_miembro) + " exitosamente"
    print("El id del nuevo rol del usuario modificado es " + str(id_rol))

    return redirect('/proyectos-miembros/' + str(id_proyecto))


@csrf_exempt
def cancelar_user_story(request, id_user_story):
    us = UserStory.objects.get(id=id_user_story)
    us.cancelado = True
    us.save()
    request.session['msg'] = "La US N° " + str(us.id) + " ha sido cancelada"
    return redirect('/productbacklog/' + str(us.proyecto.id)) @ csrf_exempt


def asignar_sprint_user_story_post(request, id_user_story):
    us = UserStory.objects.get(id=id_user_story)
    print("Asignar Sprint al User Story " + str(id_user_story) + " del proyecto " + str(us.proyecto.id))
    print(request.POST)
    post_data_json = request.POST['data']
    json_object = json.loads(post_data_json)
    id_sprint = json_object['id_sprint']
    sprint = Sprint.objects.get(id=id_sprint)
    print("El id del Sprint a asignar es -> " + str(id_sprint) + " -> " + str(sprint))
    us.sprint_asoc = sprint
    hs_aumentar_estimado = int(get_id(json_object['aumento_hs_estimado']))
    if hs_aumentar_estimado > 0:
        data = {}
        data['user_horas'] = request.user.username
        data['cant_horas'] = hs_aumentar_estimado
        data['sprint_id'] = sprint.id
        observacion = "Se aumentan las horas del US en " + str(
            hs_aumentar_estimado) + " Hs al reasignar en el Sprint N° " + str(sprint.id)
        us.agregar_evento(tipo_evento='aumento_hs', descripcion=observacion, usuario=request.user.username, data=data)
        us.estimacion_horas = us.estimacion_horas + hs_aumentar_estimado
    us.save()
    request.session['msg'] = "El Sprint N° " + str(us.sprint_asoc.id) + " ha sido asignado al US Nº " + str(us.id)
    return redirect('/asignacion-us-usuario-sprint/' + str(us.proyecto.id) + "/" + str(sprint.id))


def agregar_integrante_sprint_post(request, id_sprint):
    sprint = Sprint.objects.get(id=id_sprint)
    print("Asignar Integrante al equipo del Sprint " + str(id_sprint) + " del proyecto " + str(sprint.proyecto.id))
    print(request.POST)
    post_data_json = request.POST['data']
    json_object = json.loads(post_data_json)
    id_integrante = json_object['miembro']
    miembro = Miembro.objects.get(id=id_integrante)
    cant_horas = json_object['horas']

    integrante = Integrante()
    integrante.integrante = miembro.user
    integrante.cant_horas_dias = cant_horas

    sprint.agregar_integrante(miembro.user_id, miembro.user.username, cant_horas)
    sprint.carga_horas_diarias_equipo = sprint.calcular_capacidad_equipo_cantidad_horas()
    sprint.save()
    print("El integrante a añadir es -> " + str(id_integrante) + " con horas ->" + str(cant_horas))

    request.session['msg'] = "Se añadió el integrante -> " + str(
        id_integrante) + " - " + integrante.integrante.username + " al sprint -> " + str(sprint.id)
    return redirect('/ver-equipo-sprint/' + str(sprint.id))


def eliminar_integrante_sprint_post(request, id_sprint, id_user):
    sprint = Sprint.objects.get(id=id_sprint)
    print("Eliminar Integrante del equipo del Sprint " + str(id_sprint) + " del proyecto " + str(sprint.proyecto.id))
    sprint.eliminar_integrante(id_user)
    sprint.carga_horas_diarias_equipo = sprint.calcular_capacidad_equipo_cantidad_horas()
    sprint.save()
    request.session['msg'] = "Se elimina el integrante -> N° " + str(id_user) + " al sprint -> " + str(sprint.id)
    return redirect('/ver-equipo-sprint/' + str(sprint.id))


def asignar_usuario_us(request, id_sprint):
    # obtenemos el paquete data, con el json con los datos que necesitamos
    print('-----------PRODUCTO BACKLOG-----------')
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    print(data)
    print('-----------ID USER STORY-----------')
    id_user_story = get_id(data['id_user_story'])
    print(id_user_story)
    user_story = UserStory.objects.get(id=id_user_story)
    print(user_story.id)
    print('-----------ID USER-----------')
    print(data)
    id_user = get_id(data['usuario_asignado_id'])
    print(id_user)
    usuario = User.objects.get(id=id_user)
    print(usuario)
    user_story.usuario_asignado = usuario
    user_story.save()
    request.session['msg'] = "Se asignó al usuario " + str(usuario.username) + " al UserStory: " + str(user_story.id)
    return redirect('/asignacion-us-usuario-sprint/' + str(user_story.proyecto.id) + "/" + str(id_sprint))


def asignar_usuario_us_sprintbacklog(request):
    # obtenemos el paquete data, con el json con los datos que necesitamos
    print('-----------PRODUCTO BACKLOG-----------')
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data = json.loads(post_data_json)
    print(data)
    print('-----------ID USER STORY-----------')
    id_user_story = get_id(data['id_user_story'])
    print(id_user_story)
    user_story = UserStory.objects.get(id=id_user_story)
    print(user_story.id)
    print('-----------ID USER-----------')
    print(data)
    id_user = get_id(data['usuario_asignado_id'])
    print(id_user)
    usuario = User.objects.get(id=id_user)
    print(usuario)
    user_story.usuario_asignado = usuario
    user_story.save()
    request.session['msg'] = "Se asignó el usuario: " + str(usuario.username) + " al Sprint: " + str(
        user_story.sprint_asoc.id)
    return redirect('/sprintbacklog/' + str(user_story.sprint_asoc.id))


def actualizar_estado_us_post(request):
    # obtenemos el paquete data, con el json con los datos que necesitamos
    post_data_json = request.POST['data']
    # convertimos el string en un objeto json, que podemos acceder
    data_post = json.loads(post_data_json)
    print(data_post)
    user_story = UserStory.objects.get(id=get_id(data_post['id_user_story']))
    estado_actual = data_post['estado_actual']
    estado_fin = data_post['estado_fin']
    id_user_story = get_id(data_post['id_user_story'])

    id_us = get_id(data_post['id_user_story'])

    data = {}

    data['user_horas'] = request.user.username
    data['cant_horas'] = 0
    data['sprint_id'] = user_story.sprint_asoc.id

    observacion = data_post['evento_estado']
    user_story.agregar_evento(tipo_evento='observacion', descripcion=observacion, usuario=request.user.username,
                              data=data)

    observacion = "El estado del U.S (N° " + str(user_story.id) + ") ha pasado de " + estado_actual + " a " + estado_fin
    user_story.agregar_evento(tipo_evento='sistema', descripcion=observacion, usuario=request.user.username,
                              data=data)

    user_story.estado = estado_fin
    valor_check = data_post['finalizarUserStory']
    print("valor check-> " + str(valor_check))
    if (valor_check == True):
        user_story.finalizado = True
        observacion = "El Scrum Master ha finalizado esta tarea. "
        user_story.agregar_evento(tipo_evento='sistema', descripcion=observacion, usuario=request.user.username,
                                  data=data)

    user_story.save()

    request.session['msg'] = "El estado del U.S (N° " + str(
        user_story.id) + ") ha pasado de " + estado_actual + " a " + estado_fin
    return redirect('/ver-tablero/' + str(user_story.sprint_asoc.id) + "/" + str(user_story.nro_tipo_us()))


def eliminar_integrante_equipo(request, id_integrante, id_proyecto):
    integrante_eliminar = Integrante.objects.get(id=id_integrante)
    print("El integrante es -> " + str(integrante_eliminar))
    cant_horas = integrante_eliminar.cant_horas_dias
    print("La cantidad de horas a restar es -> " + str(cant_horas))
    integrante_eliminar.delete()
    integrantes = Integrante.objects.filter(equipo__proyecto__id=id_proyecto).select_related("integrante")
    print('-------------------')
    print(integrantes)
    print('-------------------')
    equipo = []
    cant_horas_total = 0

    for x in integrantes:
        dic = {}
        dic["nombre"] = x.integrante.username
        dic["cant_horas"] = x.cant_horas_dias
        cant_horas_total = cant_horas_total + x.cant_horas_dias
        equipo.append(dic)
    print("-----------------KLa cantidad total de horas es " + str(cant_horas_total))
    equipo_cap = Equipo.objects.get(proyecto_id=id_proyecto)
    print("El equipo del proyecto " + str(id_proyecto) + " tiene id " + str(equipo_cap.id) + "  " + str(equipo_cap))
    equipo_cap.capacidad = cant_horas_total
    equipo_cap.save()
    integrantes_json = json.dumps(equipo)
    print("El integrante a eliminar es -> " + str(id_integrante) + " del proyecto " + str(id_proyecto))
    return redirect('/proyectos-integrantes/' + str(id_proyecto))


def modificar_us_proyecto_post(request, id_proyecto_id):
    print(request.POST)
    post_data_json = request.POST['data']
    json_object = json.loads(post_data_json)
    print("VER:")
    print(json_object)
    id_tipo_us = get_id(json_object['tipouserstory'])
    print("ID TIPO US:")
    print(id_tipo_us)

    US_proyecto = Proyecto.objects.get(id=id_proyecto_id).tipos_storys
    lista_de_us_nueva = []

    if US_proyecto is not None:
        aDict = json.loads(US_proyecto)  # Transforma la lista json de US del proyecto a un diccionario
        print(aDict)
        for item in aDict:
            print(item)
            lista_de_us_nueva.append(item)

    importar_us = TipoUserStory.objects.get(id=id_tipo_us)

    dic = {}
    dic['id'] = importar_us.id
    dic['nombre'] = importar_us.descripcion
    dic['estados'] = importar_us.estados
    lista_de_us_nueva.append(dic)

    json_lista_de_us_nueva = json.dumps(lista_de_us_nueva)

    proyecto = Proyecto.objects.get(id=id_proyecto_id)
    proyecto.tipos_storys = json_lista_de_us_nueva
    proyecto.save()

    importar_us.en_uso = True
    importar_us.save()

    print("El id del proyecto es -----> " + str(id_proyecto_id))
    # miembros_proyectos = Proyecto.objects.filter(roles_de_proyecto__descripcion='DEVELOPER')
    proyecto = Proyecto.objects.get(id=id_proyecto_id)
    msg = ""
    json_lista = {}
    if (proyecto.tipos_storys is not None):
        print(proyecto.tipos_storys)
        json_lista = json.loads(proyecto.tipos_storys)
        print('se recargo la lista de storys')

    print(json_lista)
    try:
        msg = request.session['msg']
        request.session['msg'] = ''
    except:
        print('no hay session')
    return render(request, "tipostory/tipo-story-proyecto.html",
                  {"tipos_story": json_lista, "proyecto": proyecto, "msg": msg, "id_proyecto_id": id_proyecto_id})


def modificar_integrante_proyecto_post(request, id_integrante, id_proyecto):
    print(request.POST)
    post_data_json = request.POST['data']
    json_object = json.loads(post_data_json)
    cant_horas_act = json_object['horas']
    print("Nueva cantidad de horas es -> " + str(cant_horas_act))
    integrante = Integrante.objects.get(id=id_integrante)
    integrante.cant_horas_dias = cant_horas_act
    integrante.save()
    print("integrante---------------" + str(integrante))
    return redirect("/proyectos-integrantes/" + str(id_proyecto))


def eliminar_rol_sistema(request, id):
    print('Se va eliminar el rol -> ' + str(id))
    try:
        rol = RolesSistema.objects.get(id=id)
        roles_usuario = RolUsuario.objects.filter(rol=rol)
        if (len(roles_usuario) == 0):
            rol.delete()
            request.session['msg'] = "Se eliminó el rol: " + rol.descripcion
        else:
            request.session['msgerror'] = "No se puede eliminar.. actualmente el Rol es usado"
    except RolUsuario.DoesNotExist:
        rol.delete()
        request.session['msg'] = "Rol eliminado exitosamente"
    return redirect("/roles-sistema/")


def concretar_venta_contado_post(request, id):
    try:
        venta = Venta.objects.get(id=id)
        venta.estado= Estado.objects.get(id=6)
        venta.save()
        msg = "La venta se concretó y paso a proceso de entrega"
        request.session['msg'] = msg
    except Exception as e:
        msg = "Ocurrió un error al concretar la venta: " + str(e)
        request.session['msgerror'] = msg
        print(msg)  # Imprime el error en la consola
        traceback.print_exc()
    return redirect("/ventas-pendientes-modificacion/")