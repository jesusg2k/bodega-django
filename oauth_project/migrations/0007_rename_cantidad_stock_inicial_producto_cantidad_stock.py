# Generated by Django 4.1 on 2023-10-12 04:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_project', '0006_producto_is_active'),
    ]

    operations = [
        migrations.RenameField(
            model_name='producto',
            old_name='cantidad_stock_inicial',
            new_name='cantidad_stock',
        ),
    ]