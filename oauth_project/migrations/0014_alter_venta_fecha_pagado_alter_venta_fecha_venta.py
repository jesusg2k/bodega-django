# Generated by Django 4.1 on 2023-10-12 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_project', '0013_venta_pagado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venta',
            name='fecha_pagado',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='venta',
            name='fecha_venta',
            field=models.DateTimeField(null=True),
        ),
    ]
