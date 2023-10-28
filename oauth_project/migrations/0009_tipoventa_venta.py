# Generated by Django 4.1 on 2023-10-12 05:27

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('oauth_project', '0008_cliente_alter_producto_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoVenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Venta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_venta', models.DateTimeField(default=datetime.datetime(2023, 10, 12, 5, 27, 25, 110702))),
                ('fecha_pagado', models.DateTimeField(default=None)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oauth_project.cliente')),
                ('estado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oauth_project.estado')),
                ('tipo_venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oauth_project.tipoventa')),
                ('vendedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]