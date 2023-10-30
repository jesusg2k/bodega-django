"""
    oauth_project URL Configuration

"""
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path, include
from django.views.generic import TemplateView

from . import views


from .views import create_task, get_list_users, vista_form_render, view_mis_proyectos, \
    view_modificar_proyecto, view_crear_proyecto, asignar_usuario_user_story, asignar_usuario_user_story_sprintbackog, \
    VentaDetallesView

urlpatterns = [
    path('test3/', LoginView.as_view(template_name="sso.html"), name='sso'),
    path('', include('oauth_project.urls-abm')),
    ##path('test/', TemplateView.as_view(template_name="register.html"), name='test'),
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name="home.html"), name='home'),
    #path('permisos/', list_task),

    path('permisos/nuevopermiso/', create_task),
    path('test2/', LoginView.as_view(template_name="account/login.html"), name='login'),

    path('accounts/', include('allauth.urls')),


    #path('logout', LogoutView.as_view()),
    path('api/list_users', get_list_users),
    path('render/', vista_form_render),
    path('formbuilder/', vista_form_render),
    path('api/', include('oauth_project.urls-api')),
    path('misproyectos/', view_mis_proyectos),
    path('misproyectos/modificar-proyecto/', view_modificar_proyecto),
    path('misproyectos/crear-proyecto/', view_crear_proyecto, name="form-crear-proyecto"),


    ##path('misproyectos/asignar-proyecto-miembros', iniciar_proyecto),

    ##path('register/', registerPage, name="register"),
    ##path('usuarios/', view_usuarios, name="usuarios"),
    path('modificar-usuario/<int:id>', views.view_modificar_usuario, name='modificar_usuario'),
    path('modificar-equipo-proyecto/<int:id>', views.view_modificar_equipo_proyecto, name='modificar-equipo-proyecto'),


    path('register/', LoginView.as_view(template_name="register.html") , name='register'),




    path('template/', LoginView.as_view(template_name="example-template.html"), name='template-example'),
    path('test-template/', TemplateView.as_view(template_name="test-template.html"), name='test-template'),


    path('permisos/crear-permiso/', views.view_crear_permiso, name="form-crear-permiso"),


    path('roles-proyecto/crear-rol/<int:id_proyecto_id>', views.view_crear_rol, name="form-crear-rol"),
    path('roles-sistema/crear-rol/', views.view_crear_rol_sistema, name="form-crear-rol-sistema"),
    path('roles-proyecto/importar-rol/<int:id_proyecto_id>', views.view_importar_rol, name="form-importar-rol"),
    path('roles-proyecto/modificar-rol/<int:id>/<int:id_proyecto_id>', views.view_modificar_rol, name="form-modificar-rol"),
    path('roles-proyecto/<int:id_proyecto_id>', views.view_roles_proyecto, name='roles-proyecto'),
    path('actualizar-roles-proyecto/<int:id>', views.view_actualizar_permisos_rol_proyecto, name='form-actualizar-roles-proyecto'),
    path('proyectos-miembros/<int:id_proyecto>', views.view_miembros_proyecto, name='proyectos-miembros'),
    path('proyectos-integrantes/<int:id_proyecto>', views.view_equipo_proyecto, name='proyectos-integrantes'),




    path('tipos-story-proyecto/<int:id_proyecto>', views.view_tipos_story_proyecto, name='tipos-user-story-proyecto'),
    path('sprints/<int:id_proyecto>', views.view_sprints_proyecto, name='sprints-proyecto'),
    path('burndownchart/<int:id_proyecto>', views.view_proyecto_burdown_chart, name='burndown-proyecto'),

    path('productbacklog/<int:id_proyecto>', views.view_producto_backlog, name='product-backlog'),
    path('asignacion-us-usuario-sprint/<int:id_proyecto>/<int:id_sprint>', views.view_asignacion_us_usuario_sprint, name='asignacion-us-usuario-sprint'),
    path('productbacklog-finalizado/<int:id_proyecto>', views.view_producto_backlog_finalizado, name='product-backlog-finalizado'),
    path('productbacklog-pendiente/<int:id_proyecto>', views.view_producto_backlog_pendiente, name='product-backlog-pendiente'),
    path('productbacklog-sin-sprint/<int:id_proyecto>', views.view_producto_backlog_no_asignado_sprint, name='product-backlog-sin-sprint-asignado'),
    path('productbacklog-sin-usuario-asignado/<int:id_proyecto>', views.view_producto_backlog_no_asignado_usuario, name='product-backlog-sin-usuario-asignado'),

    path('sprintbacklog/<int:id_sprint>', views.view_sprint_backlog, name='sprint-backlog'),
    path('sprintbacklog-finalizado/<int:id_sprint>', views.view_sprint_backlog_finalizado, name='sprint-backlog-finalizado'),
    path('sprintbacklog-pendiente/<int:id_sprint>', views.view_sprint_backlog_pendiente, name='sprint-backlog-pendiente'),
    path('sprintbacklog-sin-usuario/<int:id_sprint>', views.view_sprint_backlog_sin_usuario_asignado, name='sprint-backlog-sin-usuario'),



    path('informe-sprint-actual/<int:id_sprint>', views.view_informe_sprint_actual, name='informe-sprint-actual'),
    path('informe-sprint-historico/<int:id_sprint>', views.view_informe_sprint_historico, name='informe-sprint-historico'),

    path('proyectos-miembros/agregar_miembro/<int:id_proyecto>', views.view_asignar_miembro, name='agregar-miembro-proyecto'),
    path('modificar-tipo-story-get/<int:id>', views.view_actualizar_tipo_user_story, name='modificar-tipo-story-get'),
    path('tipos-story-proyecto/importar-tipo-us/<int:id_proyecto_id>', views.view_importar_tipos_user_story , name="form-importar-tipo-us"),
    path('proyectos-miembros/agregar_miembro/<int:id_proyecto>', views.view_crear_miembros, name='agregar-miembro-proyecto'),
    path('proyectos-miembros/modificar_miembro/<int:id_miembro>/<int:id_proyecto>', views.view_modificar_miembro, name='form-modificar-miembro-proyecto'),





    path('crear-sprint/<int:id_proyecto>', views.agregar_sprint_proyecto, name='agregar-sprint-proyecto'),
    path('modificar-sprint-default/<int:id_sprint>/<int:id_proyecto>', views.modificar_sprint_default_proyecto, name='modificar-sprint-default'),
    path('ver-equipo-sprint/<int:id_sprint>', views.view_equipo_sprint, name='view_equipo_sprint'),
    path('ver-eventos-user-story/<int:id_user_story>', views.ver_eventos_user_story, name='ver-eventos-user-story'),
    path('agregar-integrante-sprint/<int:id_sprint>', views.view_agregar_integrante_sprint, name='agregar-integrante-sprint'),
    path('productbacklog/asignar-usuario-user-story/<int:id_user_story>/<int:id_sprint>', asignar_usuario_user_story, name='asignar-usuario-user-story'),

    path('productbacklog/asignar-sprint-user-story/<int:id_user_story>/<int:id_sprint>', views.view_asignar_sprint_user_story, name='view-asignar-sprint-user-story'),




    path('modificar-integrantes/<int:id_integrante>/<int:id_proyecto>', views.view_modificar_integrante_proyecto, name='modificar-integrantes'),
    path('crear-integrantes/<int:id_proyecto>', views.view_integrantes_proyecto, name='crear-integrantes'),

    path('agregar-us-proyecto/<int:id_proyecto>', views.agregar_us_proyecto, name='agregar-us-proyecto'),
    path('ver-tablero/<int:id_sprint>/<int:nro_tipo_user>', views.ver_tablero_kanban, name='ver-tablero-kanban'),
    path('registrar-actividad/<int:id_user_story>', views.registrar_actividad_us, name='registrar-actividad-us'),
    path('actualizar-estado/<int:id_user_story>', views.actualizar_estado_us, name='actualizar-estado-us'),
    path('actualizar_rol_usuario/<int:id_usuario>', views.actualizar_rol_usuario, name='actualizar_rol_usuario'),
    path('actualizar_producto/<int:id>', views.actualizar_producto, name='actualizar_producto'),
    path('lista_precios/<int:id>', views.ver_lista_precios, name='ver_lista_precios'),
    path('actualizar_cliente/<int:id>', views.actualizar_cliente, name='actualizar_cliente'),
    path('actualizar_categoria/<int:id>', views.actualizar_categoria, name='actualizar_categoria_get'),
    path('usuarios/crear-usuario-sistema', views.form_crear_usuario_sistema, name='crear-form-usuario-sistema'),
    path('categorais/crear-categoria', views.form_crear_categoria, name='crear-form-categoria'),
    path('lista_precios/crear_precio/<int:id>', views.form_crear_precio, name='agregar_precio_form'),
    path('lista_precios/modificar/<int:id>', views.form_modificar_precio, name='modificar_precio_get'),
    path('tipospago/crear-tipo-pago', views.form_crear_tipo_pago, name='crear-form-tipo-pago'),
    path('actualizar_tipopago/<int:id>', views.actualizar_tipo_pago, name='actualizar_tipo_pago_get'),
    path('devoluciones/crear', views.form_devoluciones_crear, name='devoluciones_crear'),
    path('ventas/crear-venta', views.crear_form_venta, name='crear_form_venta'),
    path('ventas/crear-venta/contado', views.crear_form_venta_contado, name='crear_form_venta_contado'),
    path('actualizar_venta_contado/<int:id>/', views.actualizar_venta_contado, name='actualizar_venta_contado'),
    path('ver_venta_para_concretar/<int:id>/', views.ver_venta_para_concretar, name='ver_venta_para_concretar'),
    path('productos/crear-producto', views.form_crear_producto, name='form_crear_producto'),
    path('clientes/crear-cliente', views.form_crear_cliente, name='form_crear_cliente'),
    path('venta-detalles/<int:id>/', VentaDetallesView.as_view(), name='venta-detalles'),
    path('<filename>/', views.html),
    path('', views.index)
]

urlpatterns += staticfiles_urlpatterns()

