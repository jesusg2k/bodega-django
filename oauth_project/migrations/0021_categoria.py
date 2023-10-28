# Generated by Django 3.2.6 on 2023-10-22 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_project', '0020_devolucion_cliente'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField()),
                ('is_activo', models.BooleanField(default=True)),
            ],
        ),
    ]
