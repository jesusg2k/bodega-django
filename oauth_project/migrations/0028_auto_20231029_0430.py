# Generated by Django 3.2.6 on 2023-10-29 04:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_project', '0027_precioproducto'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='producto',
            name='precio_intermedio',
        ),
        migrations.RemoveField(
            model_name='producto',
            name='precio_mayorista',
        ),
        migrations.RemoveField(
            model_name='producto',
            name='precio_minorista',
        ),
    ]
