INSERT INTO public.oauth_project_estado (id, descripcion) VALUES(1, 'CREADO');
INSERT INTO public.oauth_project_estado (id, descripcion) VALUES(2, 'INICIADO');
INSERT INTO public.oauth_project_estado (id, descripcion) VALUES(3, 'FINALIZADO');
INSERT INTO public.oauth_project_estado (id, descripcion) VALUES(4, 'CANCELADO');

insert into oauth_project_permiso (id, descripcion) values (1,'iniciar-proyecto');
insert into oauth_project_permiso (id, descripcion) values (2,'finalizar-proyecto');
insert into oauth_project_permiso (id, descripcion) values (3,'cancelar-proyecto');
insert into oauth_project_permiso (id, descripcion) values (4,'ver-equipo');
insert into oauth_project_permiso (id, descripcion) values (5,'ver-roles');
insert into oauth_project_permiso (id, descripcion) values (6,'crear-rol');
insert into oauth_project_permiso (id, descripcion) values (7,'modificar-rol');
insert into oauth_project_permiso (id, descripcion) values (8,'modificar-permisos-rol');
insert into oauth_project_permiso (id, descripcion) values (9,'ver-miembros');
insert into oauth_project_permiso (id, descripcion) values (10,'crear-miembro');
insert into oauth_project_permiso (id, descripcion) values (11,'modificar-miembro');
insert into oauth_project_permiso (id, descripcion) values (12,'eliminar-miembro');
insert into oauth_project_permiso (id, descripcion) values (13,'ver-product-backlog');
insert into oauth_project_permiso (id, descripcion) values (14,'agregar-us-product-backlog');
insert into oauth_project_permiso (id, descripcion) values (15,'ver-sprint');
insert into oauth_project_permiso (id, descripcion) values (16,'crear-sprint');
insert into oauth_project_permiso (id, descripcion) values (17,'cancelar-us-story');
insert into oauth_project_permiso (id, descripcion) values (18,'iniciar-sprint');
insert into oauth_project_permiso (id, descripcion) values (19,'finalizar-sprint');
insert into oauth_project_permiso (id, descripcion) values (20,'cancelar-sprint');
insert into oauth_project_permiso (id, descripcion) values (21,'ver-tablero-kanban');
insert into oauth_project_permiso (id, descripcion) values (22,'agregar-integrante-sprint');
insert into oauth_project_permiso (id, descripcion) values (23,'ver-sprint-backlog');
insert into oauth_project_permiso (id, descripcion) values (24,'ver-equipo-sprint');
insert into oauth_project_permiso (id, descripcion) values (25,'modificar-sprint');
insert into oauth_project_permiso (id, descripcion) values (26,'ver-spring-informe');
insert into oauth_project_permiso (id, descripcion) values (27,'eliminar-integrante-spring');
insert into oauth_project_permiso (id, descripcion) values (28,'actualizar-estado-us-tablero');
insert into oauth_project_permiso (id, descripcion) values (29,'asignaciones-product-backlog');



insert into oauth_project_rolproyecto (id, descripcion, proyecto_id) values (600, 'PERSONALIZADO',1);
insert into oauth_project_rolproyecto (id, descripcion, proyecto_id) values (601, 'OBSERVADOR',1);
insert into oauth_project_rolproyecto (id, descripcion, proyecto_id) values (602, 'CLIENTE',1);

insert into oauth_project_permisorol (permiso_id, rol_id) values (1,600);
insert into oauth_project_permisorol (permiso_id, rol_id) values (2,600);
insert into oauth_project_permisorol (permiso_id, rol_id) values (3,600);
insert into oauth_project_permisorol (permiso_id, rol_id) values (4,600);

insert into oauth_project_permisorol (permiso_id, rol_id) values (4,601);
insert into oauth_project_permisorol (permiso_id, rol_id) values (5,601);
insert into oauth_project_permisorol (permiso_id, rol_id) values (9,601);
insert into oauth_project_permisorol (permiso_id, rol_id) values (13,601);
insert into oauth_project_permisorol (permiso_id, rol_id) values (15,601);

insert into oauth_project_permisorol (permiso_id, rol_id) values (13,602);


