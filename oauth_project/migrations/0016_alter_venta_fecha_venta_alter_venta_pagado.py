# Generated by Django 4.1 on 2023-10-12 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_project', '0015_alter_venta_pagado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venta',
            name='fecha_venta',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='venta',
            name='pagado',
            field=models.BooleanField(default=False),
        ),
    ]
