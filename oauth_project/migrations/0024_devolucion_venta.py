# Generated by Django 3.2.6 on 2023-10-28 14:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_project', '0023_devolucion_monto_devolucion'),
    ]

    operations = [
        migrations.AddField(
            model_name='devolucion',
            name='venta',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='oauth_project.venta'),
            preserve_default=False,
        ),
    ]