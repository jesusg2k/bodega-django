# Generated by Django 4.1 on 2023-10-08 03:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_project', '0003_rolusuario'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rolusuario',
            name='descripcion',
        ),
        migrations.AddField(
            model_name='rolusuario',
            name='rol',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='oauth_project.rolessistema'),
            preserve_default=False,
        ),
    ]
