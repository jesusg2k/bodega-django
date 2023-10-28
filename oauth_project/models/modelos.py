
import json

from django.template.backends import django
from django.utils import timezone
from datetime import datetime
import datetime as datetimex

from django.contrib.auth.models import User
from django.db import models, utils
from django.conf import settings
from django.db.models import Q
from django.db.models.signals import post_save
from django.http import Http404
from django.urls import reverse

from oauth_app import admin
# V
class Permiso(models.Model):
    descripcion = models.TextField(blank=True)


# V
class Estado(models.Model):
    descripcion = models.TextField(blank=True)
    def _str_(self):
        return str(self.id) +" - "+ str(self.nombre)


# V
class Proyecto(models.Model):
    nombre_proyecto = models.TextField(blank=True)
    descripcion = models.TextField(blank=True)
    scrum_master = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_inicio = models.DateField(null=True)
    fecha_fin = models.DateField(null=True)
    creado_by = models.IntegerField(null=False)
    estado = models.ForeignKey(Estado, null=False, on_delete=models.CASCADE)
    tipos_storys = models.JSONField(null=True)

    def lista_us_text(self):
        tipos_json = json.loads(self.tipos_storys)
        lista_tipos_text = ""
        for t in tipos_json:
            lista_tipos_text = lista_tipos_text +str(t['id'])+" - "+str(t['nombre'])+"\n"
        return lista_tipos_text
    def capacidad_hora_diaria_equipo(self):
        integrantes = Integrante.objects.filter(equipo__proyecto_id=self.id)
        cant_horas = 0
        for x in integrantes:
            cant_horas = cant_horas + x.cant_horas_dias
        return cant_horas

    def cantidad_integrantes_equipo(self):
        return Integrante.objects.filter(equipo__proyecto_id=self.id).count()

class Equipo(models.Model):
    proyecto = models.ForeignKey(Proyecto, null=False, on_delete=models.CASCADE)
    capacidad = models.IntegerField(default=0)




# V
class Integrante(models.Model):
    integrante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipo, null=False, on_delete=models.CASCADE)
    cant_horas_dias = models.IntegerField(default=0)

class RolProyecto(models.Model):
    descripcion = models.TextField(blank=True)
    proyecto = models.ForeignKey(Proyecto, null=False, on_delete=models.CASCADE)


class Miembro(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rol = models.ForeignKey(RolProyecto, null=False, on_delete=models.CASCADE)

class PermisoRol(models.Model):
    permiso = models.ForeignKey(Permiso, null=False, on_delete=models.CASCADE)
    rol = models.ForeignKey(RolProyecto, null=False, on_delete=models.CASCADE)

class Sprint(models.Model):
    descripcion = models.TextField(blank=True) #form crear este
    equipo = models.JSONField() #no
    nro_sprint = models.IntegerField() #si
    objetivo = models.TextField() #si
    fecha_inicio = models.DateField(null=True) #no
    cant_dias_duracion = models.IntegerField() #si
    fecha_fin = models.DateField(null=True) #no
    carga_horas_sprint_total = models.IntegerField(null=True) #no
    carga_horas_diarias_equipo = models.IntegerField(null=True) #no
    estado = models.ForeignKey(Estado, null=False, on_delete=models.CASCADE) #no
    proyecto = models.ForeignKey(Proyecto, null=False, on_delete=models.CASCADE) #no
    tipos_storys = models.JSONField() #no
    json_informe_historico_finalizacion = models.JSONField(null=True) #no

    def get_datos_informe(self):
        datos = {}
        cantidad_tareas = UserStory.objects.filter(sprint_asoc_id=self.id).count()
        datos['cantidad_tareas'] = cantidad_tareas
        if (cantidad_tareas > 0):
            cantidad_tareas_finalizadas = UserStory.objects.filter(sprint_asoc_id=self.id, finalizado=True).count()
            cantidad_tareas_pendientes = UserStory.objects.filter(sprint_asoc_id=self.id, finalizado=False).count()
            datos['cantidad_tareas_finalizadas'] = cantidad_tareas_finalizadas
            datos['cantidad_tareas_pendientes'] = cantidad_tareas_pendientes
            porc_tareas_finalizadas = round(cantidad_tareas_finalizadas / cantidad_tareas * 100)
            porc_tareas_pendientes = round(cantidad_tareas_pendientes / cantidad_tareas * 100)
            datos['porc_tareas_finalizadas'] = porc_tareas_finalizadas
            datos['porc_tareas_pendientes'] = porc_tareas_pendientes

        datos['trabajo_total_us_en_horas_sprint'] = self.horas_total_estimadas_us()
        datos['capacidad_diaria_equipo'] = self.carga_horas_diarias_equipo
        dias_estimado_terminar_tareas = self.cant_dias_estimados()

        datos['dias_estimado_terminar_tareas'] = self.cant_dias_estimados()
        datos['duracion_sprint_dias'] = self.cant_dias_duracion

        fecha_inicio_sprint = self.fecha_inicio
        datos['fecha_inicio_sprint'] = fecha_inicio_sprint
        fecha_planificada_fin_sprint = fecha_inicio_sprint + datetimex.timedelta(days=int(self.cant_dias_duracion))
        fecha_planificado_tmp = timezone.now().replace(*(*fecha_planificada_fin_sprint.timetuple()[:6], 0))

        datos['fecha_planificada_fin_sprint'] = fecha_planificada_fin_sprint
        print(type(fecha_planificada_fin_sprint))
        fecha_ahora_date = (datetimex.datetime.now() - datetimex.timedelta(days=0))
        naive = fecha_planificado_tmp.replace(tzinfo=None)
        datos['dias_restantes_planif'] = (naive - fecha_ahora_date).days

        print(dias_estimado_terminar_tareas)
        print(type(dias_estimado_terminar_tareas))
        dias_extras = datetimex.timedelta(days=int(dias_estimado_terminar_tareas))
        fecha_estimada_fin_sprint = fecha_inicio_sprint + dias_extras
        datos['fecha_estimada_fin_sprint'] = fecha_estimada_fin_sprint
        if (fecha_planificada_fin_sprint >= fecha_estimada_fin_sprint):
            datos['dias_de_retraso'] = 0
        else:
            datos['dias_de_retraso'] = (fecha_estimada_fin_sprint - fecha_planificada_fin_sprint).days

        datos['fecha_fin_oficial_sprint'] = self.fecha_fin

        equipo = []
        equipo_json_equipo = json.loads(self.equipo)
        cant_tarea_asignada = UserStory.objects.filter(sprint_asoc_id=self.id, usuario_asignado__isnull=False).count()
        datos['cant_tarea_asignada'] = cant_tarea_asignada
        for inte in equipo_json_equipo:
            dic = {}
            dic['id'] = inte['id']
            dic['nombre'] = inte['nombre']
            dic['cant_horas'] = inte['cant_horas']
            print('se van a buscar las tareas del sprint N° -> '+str(self.id))
            dic['cant_tareas_asignadas'] = UserStory.objects.filter(sprint_asoc_id=self.id,
                                                                    usuario_asignado=inte['id']).count()
            if (cant_tarea_asignada > 0):
                dic['porc_tarea_realizada'] = round(dic['cant_tareas_asignadas'] / cant_tarea_asignada * 100)
            else:
                dic['porc_tarea_realizada'] = 0
            equipo.append(dic)

        datos['equipo_integrantes'] = equipo

        lista_us_sprint = UserStory.objects.filter(sprint_asoc_id=self.id)

        cant_evento_observaciones = 0
        cant_evento_hs_aumentada = 0
        cant_evento_registro_horas = 0

        observaciones_registradas = []
        trabajos_registrados = []
        aumento_hs_registrados = []

        cant_horas_registradas_sprint = 0
        cant_horas_aumentadas = 0

        cantidad_us_retradas = 0
        us_retrasados = []

        for us in lista_us_sprint:
            map_eventos_obs = us.cantidad_EVENTO_generico_sprint(sprint_id=self.id, evento="observacion")
            map_eventos_aumento_hs = us.cantidad_EVENTO_generico_sprint(sprint_id=self.id, evento="aumento_hs")
            map_eventos_registro_horas = us.cantidad_EVENTO_generico_sprint(sprint_id=self.id, evento="registro_horas")

            cant_evento_observaciones = cant_evento_observaciones + map_eventos_obs['cantidad_eventos']
            cant_evento_hs_aumentada = cant_evento_hs_aumentada + map_eventos_aumento_hs['cantidad_eventos']
            cant_evento_registro_horas = cant_evento_registro_horas + map_eventos_registro_horas['cantidad_eventos']
            print("-----------cantidad obs-----------")
            print(cant_evento_observaciones)
            print(len(map_eventos_obs['registros']))
            cant_horas_aumentadas = cant_horas_aumentadas + map_eventos_aumento_hs['cantidad_horas']
            cant_horas_registradas_sprint = cant_horas_registradas_sprint + map_eventos_registro_horas['cantidad_horas']

            for x in map_eventos_obs['registros']:
                observaciones_registradas.append(x)
            for x in map_eventos_aumento_hs['registros']:
                aumento_hs_registrados.append(x)
            for x in map_eventos_registro_horas['registros']:
                trabajos_registrados.append(x)

            map_eventos_registro_retrasado = us.cantidad_EVENTO_generico_sprint(evento="registro_horas")
            if (us.estimacion_horas < map_eventos_registro_retrasado['cantidad_horas']):
                cantidad_us_retradas = cantidad_us_retradas + 1
                us_retrasados.append(us)

            datos['cant_evento_observaciones'] = cant_evento_observaciones
            datos['cant_evento_hs_aumentada'] = cant_evento_hs_aumentada
            datos['cant_evento_registro_horas'] = cant_evento_registro_horas
            datos['observaciones_registradas'] = observaciones_registradas
            datos['trabajos_registrados'] = trabajos_registrados
            datos['aumento_hs_registrados'] = aumento_hs_registrados
            datos['cant_horas_registradas_sprint'] = cant_horas_registradas_sprint
            datos['cant_horas_aumentadas'] = cant_horas_aumentadas
            datos['cantidad_us_retradas'] = cantidad_us_retradas
            datos['us_retrasados'] = us_retrasados

        return datos

    def agregar_integrante(self,id_integrante, nombre_usuario, cant_horas_diarias):
        json_equipo = json.loads(self.equipo)
        n = len(json_equipo)
        print("El equipo json en el metodo agregar_integrante es-> ")
        print(json_equipo)
        dic = {}
        dic['id'] = id_integrante
        dic['nombre'] = nombre_usuario
        dic['cant_horas'] = cant_horas_diarias
        json_equipo.append(dic)
        print("json.dumps -> "+str(json_equipo))
        self.equipo = json.dumps(json_equipo)

    def eliminar_integrante(self, id_user):
        json_equipo = json.loads(self.equipo)
        n = len(json_equipo)
        print("El equipo json en el metodo eliminar_integrante es-> ")
        print(json_equipo)
        nueva_lista = []
        for x in json_equipo:
            print("se compara el id de cada integrante del equipo con el id_user recibido")
            print(str(x['id'])+" -> "+str(id_user))
            if x['id'] != id_user:
                nueva_lista.append(x)
                #break
        self.equipo = json.dumps(nueva_lista)

    def calcular_capacidad_equipo_cantidad_horas(self):
        cant_horas = 0
        json_equipo = json.loads(self.equipo)
        n = len(json_equipo)
        print("El equipo json en el metodo eliminar_integrante es-> ")
        print(json_equipo)
        for x in json_equipo:
            cant_horas = cant_horas + x['cant_horas']
        return cant_horas

    def calcular_numero_integrantes_equipo(self):
        cant_horas = 0
        json_equipo = json.loads(self.equipo)
        n = len(json_equipo)
        return n

    def lista_equipo_text(self):
        lista_equipo = ""
        json_equipo = json.loads(self.equipo)
        for integrante in json_equipo:
            lista_equipo = lista_equipo +integrante['nombre'] +", "
        return lista_equipo

    def tipo_user_story_text(self):
        lista_tipo_us = ""
        lista_tipo_us_json = json.loads(self.tipos_storys)
        for tipo_us in lista_tipo_us_json:
            lista_tipo_us = lista_tipo_us +str(tipo_us['id'])+" - "+tipo_us['nombre'] +"\n "
        return lista_tipo_us

    def horas_total_estimadas_us(self):
        dic = {}
        cant_horas_estimadas = 0
        lista_us = UserStory.objects.filter(sprint_asoc__id=self.id)
        for us in lista_us:
            cant_horas_estimadas = cant_horas_estimadas + us.estimacion_horas
        dic['cant_horas'] = cant_horas_estimadas
        dic['cant_us'] = len(lista_us)
        return dic

    def cant_dias_estimados(self):
        cant_horas_estimadas = self.horas_total_estimadas_us()
        capacidad_equipo = self.calcular_capacidad_equipo_cantidad_horas()
        if(capacidad_equipo==0):
            return -1

        if(capacidad_equipo>cant_horas_estimadas['cant_horas']):
            return 1

        return round(cant_horas_estimadas['cant_horas']/capacidad_equipo)



class TipoUserStory(models.Model):
    descripcion = models.TextField(blank=False)
    en_uso = models.BooleanField(default=False)
    estados = models.JSONField()

class UserStory(models.Model):
    descripcion = models.TextField(blank=False)
    detalles = models.TextField(blank=False)
    user_point = models.SmallIntegerField()
    business_value = models.SmallIntegerField()
    estado = models.TextField(blank=False)
    tipo_user_story = models.ForeignKey(TipoUserStory, null=False, on_delete=models.CASCADE)
    sprint_asoc = models.ForeignKey(Sprint, null=True, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, null=False, on_delete=models.CASCADE)
    estimacion_horas = models.IntegerField()
    estimacion_horas_inicial = models.IntegerField()
    eventos = models.JSONField()
    usuario_asignado = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    cancelado = models.BooleanField(default=False)
    finalizado = models.BooleanField(default=False)
    def prioridad(self):
        PN = 0.6 * self.business_value
        PT = 0.4 * self.user_point
        PS = 0
        if self.sprint_asoc is None:
            cantidad_horas = self.cantidad_horas_registras_sprint()
            if( cantidad_horas > 0):
                PS = 3
            else:
                PS = 0
        else:
            cant_horas_sprint = self.cantidad_horas_registras_sprint(sprint_id=self.sprint_asoc.id)
            cant_total_trabajo = self.cantidad_horas_registras_sprint()
            if(cant_total_trabajo> cant_horas_sprint):
                PS = 3
            else:
                PS = 0
        return round(((PN + PT) / 2)+PS)

    def primera_fecha(self):
        return UserStory.fechas_primero_ultimo(self)['primera_fecha']

    def ultima_fecha(self):
        return UserStory.fechas_primero_ultimo(self)['ultima_fecha']
    def fechas_primero_ultimo(self):
        json_eventos = json.loads(self.eventos)
        n = len(json_eventos)
        fecha = json_eventos[0]
        primera_fecha = None
        ultima_fecha = None
        for x in json_eventos:
            if primera_fecha is None:
                primera_fecha = datetime.strptime(x['fecha'], "%d-%m-%Y (%H:%M)")
            ultima_fecha = datetime.strptime(x['fecha'], "%d-%m-%Y (%H:%M)")
        fechas_tarea = {}
        fechas_tarea['primera_fecha'] = primera_fecha
        fechas_tarea['ultima_fecha'] = ultima_fecha
        return fechas_tarea

    def agregar_evento(self, tipo_evento, descripcion, usuario, data):
        json_eventos = json.loads(self.eventos)
        n = len(json_eventos)
        print(json_eventos)
        time = datetime.now()
        fecha = time.strftime("%d-%m-%Y (%H:%M)")
        dic = {}
        dic['tipo_evento'] = tipo_evento
        dic['fecha'] = fecha
        dic['descripcion'] = descripcion
        dic['usuario'] = usuario
        dic['data'] = data
        json_eventos.append(dic)
        self.eventos = json.dumps(json_eventos)

    def cantidad_observaciones_registradas(self):
        if( self.eventos is not None):
            json_eventos = json.loads(self.eventos)
            return len(json_eventos)
        else:
            return 0







    def cantidad_EVENTO_generico_sprint(self, sprint_id = -1, evento = ""):
        print('--------- INICIO BUSQUEDA EN EVENTO ----------- '+evento)
        #print('se va calcular con el sprint_id -> '+str(sprint_id))
        map = {}
        registros = []

        cantidad_eventos = 0
        cantidad_horas = 0
        if (self.eventos is not None):
            json_eventos = json.loads(self.eventos)
            for reg in json_eventos:
                if reg['tipo_evento'] == evento:
                    data = reg['data']
                    if sprint_id > 0:
                        if data['sprint_id'] == sprint_id:
                            print(cantidad_eventos)
                            cantidad_eventos = cantidad_eventos +1
                            print(reg)
                            registros.append(reg)
                            cantidad_horas += int(data['cant_horas'])
                    else:
                        registros.append(reg)
                        cantidad_eventos = cantidad_eventos + 1
                        cantidad_eventos += int(data['cant_horas'])
            map['cantidad_eventos'] = cantidad_eventos
            map['cantidad_horas'] = cantidad_horas
            map['registros'] = registros
            print('--------- FIN BUSQUEDA EN EVENTO ----------- ' + evento)
            return map
        else:
            return 0
    def cantidad_horas_aumentadas_sprint(self, sprint_id = -1):
        print('se va calcular con el sprint_id -> '+str(sprint_id))
        if (self.eventos is not None):
            cant_horas = 0
            json_eventos = json.loads(self.eventos)
            for reg in json_eventos:
                if reg['tipo_evento'] == 'aumento_hs':
                    data = reg['data']
                    print(data)
                    if sprint_id > 0:
                        if data['sprint_id'] == sprint_id:
                            cant_horas += int(data['cant_horas_aumento'])
                    else:
                        cant_horas += int(data['cant_horas'])
            return cant_horas
        else:
            return 0



    def cantidad_horas_registras_sprint(self, sprint_id = -1):
        print('se va calcular con el sprint_id -> '+str(sprint_id))
        if (self.eventos is not None):
            cant_horas = 0
            json_eventos = json.loads(self.eventos)
            for reg in json_eventos:
                if reg['tipo_evento'] == 'registro_horas':
                    data = reg['data']
                    print(data)
                    if sprint_id > 0:
                        if data['sprint_id'] == sprint_id:
                            cant_horas += int(data['cant_horas'])
                    else:
                        cant_horas += int(data['cant_horas'])
            return cant_horas
        else:
            return 0



    def nro_tipo_us(self):
        if (self.proyecto.tipos_storys is not None):
            print(self.proyecto.id)
            json_lista_storys = json.loads(self.proyecto.tipos_storys)
            print(json_lista_storys)
            i = 0
            for n in json_lista_storys:
                print("n[id] ->"+ str(n['id']))
                print("self.tipo_user_story.id ->" + str(self.tipo_user_story.id))
                if n['id'] == self.tipo_user_story.id:
                    print('se retorna por el igual')
                    return i
                i = i+1
        return -1










class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    def _str_(self):
        return str(self.user)
    def verificar_permiso(self, id_user, id_proyecto, permiso_verif):
        proyecto = Proyecto.objects.get(id=id_proyecto)
        if(proyecto.scrum_master.id == id_user):
            print("TIENE PERMISO POR SER EL SCRUM MASTER")
            return True
        if (proyecto.creado_by == id_user):
            print("TIENE PERMISO POR SER EL CREADOR DEL PROYECTO")
            return True
        print('entro -------------')
        print('user id->' + str(id_user))
        permisos = PermisoRol.objects.filter(rol__miembro__user_id=id_user).select_related("permiso", "rol", "rol__proyecto")
        print(len(permisos))
        dic = []
        map_permisos = {}
        for x in permisos:
            permiso = 'P-' + str(x.rol.proyecto.id) +'-'+ x.permiso.descripcion
            dic.append(permiso)
            map_permisos[permiso] = True
        print('la lista cantidad de permisos son: ' + str(len(dic)))
        print('la lista de permisos es: ' + str(dic))
        p_verif = 'P-'+str(id_proyecto)+'-'+permiso_verif
        print('_-----------------')
        print('Se va consultar el permiso '+str(p_verif))
        print('_-----------------')
        if p_verif in dic:
            print('TIENE EL PERMISO '+permiso_verif+" EN EL PROYECTO "+str(id_proyecto))
            return True
        else:
            print('NEGATIVO, NO TIENE EL PERMISO ' + permiso_verif + " EN EL PROYECTO"+str(id_proyecto))
            return False








    def get_diccionario_permisos(self, id_user):
            listadepermisos = Permiso.objects.all()
            listadeproyectos = Proyecto.objects.all()

            dic = {}
            for proyecto in listadeproyectos:
                dic[proyecto.id] = {}
                for permiso in listadepermisos:
                    if proyecto.scrum_master.id == id_user:
                        dic[proyecto.id][permiso.id] = True
                    else:
                        dic[proyecto.id][permiso.id] = False



            listapermisorol = PermisoRol.objects.filter(rol__miembro__user_id=id_user).select_related("permiso", "rol",
                                                                                               "rol__proyecto")

            for permiso in listapermisorol:
                dic[permiso.rol.proyecto.id][permiso.permiso.id] = True


            return dic





    def get_lista_permisos(self, id_user):
        print('entro -------------')
        print('user id->'+str(id_user))
        permisos = PermisoRol.objects.filter(rol__miembro__user_id=id_user)
        print(len(permisos))
        dic = []

        for x in permisos:
            permiso = 'P' + str(id_user) +'-'+ x.permiso.descripcion
            dic.append(permiso)
        print('la lista cantidad de permisos son: ' + str(len(dic)))
        print('la lista de permisos es: ' + str(dic))
        return dic


class RestriccionPorPermiso(object):
    """
    A middleware that restricts staff members access to administration panels.
    """

    def restriction_process(self, request, id_proyecto, permiso_verif):
            profile = Profile()
            for x in permiso_verif:
                if not profile.verificar_permiso(request.user.id, id_proyecto, x):
                    return False
            return True


class RolesSistema(models.Model):
    descripcion = models.TextField(blank=True)

class RolUsuario(models.Model):
    rol = models.ForeignKey(RolesSistema, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Producto(models.Model):
    descripcion = models.TextField(blank=False)
    precio_minorista = models.IntegerField(blank=False)
    precio_intermedio = models.IntegerField(blank=False)
    precio_mayorista = models.IntegerField(blank=False)
    cantidad_stock = models.IntegerField(blank=False)
    is_active = models.BooleanField(blank=False, default=True)

class Cliente(models.Model):
    nombre = models.TextField(blank=False)
    telefono = models.TextField(blank=False)
    documento = models.TextField(blank=False)
    is_active = models.BooleanField(blank=False, default=True)
    def _str_(self):
        return str(self.id) +" - "+ str(self.nombre)

class TipoVenta(models.Model):
    descripcion = models.TextField(blank=True)

class Venta(models.Model):
    estado = models.ForeignKey(Estado, null=False, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, null=False, on_delete=models.CASCADE)
    tipo_venta = models.ForeignKey(TipoVenta, null=False, on_delete=models.CASCADE)
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE)
    fecha_venta = models.DateTimeField(null=False)
    fecha_pagado = models.DateTimeField(null=True)
    cantidad_articulos = models.IntegerField()
    monto_total = models.IntegerField()
    pagado = models.BooleanField()

class DetalleVenta(models.Model):
    producto = models.ForeignKey(Producto, null=False, on_delete=models.CASCADE)
    venta = models.ForeignKey(Venta, null=False, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.IntegerField()
    precio_total = models.IntegerField()
    is_precio_especial = models.BooleanField()

class Devolucion(models.Model):
    motivo_devolucion: models.TextField(blank=False)
    fecha_devolucion = models.DateTimeField(null=False)
    is_activo = models.BooleanField(default=True)
    producto = models.ForeignKey(Producto, null=False, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, null=False, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

class Categoria (models.Model):
    nombre = models.TextField(blank=False)
    is_activo = models.BooleanField(default=True)

class TipoPago (models.Model):
    nombre = models.TextField(blank=False)
    is_activo = models.BooleanField(default=True)