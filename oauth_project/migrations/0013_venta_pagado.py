# Generated by Django 4.1 on 2023-10-12 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_project', '0012_venta_cantidad_articulos_venta_monto_total_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='venta',
            name='pagado',
            field=models.BooleanField(default=False),
        ),
    ]
