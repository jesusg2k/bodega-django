# Generated by Django 4.1 on 2023-10-12 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_project', '0005_producto'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='is_active',
            field=models.IntegerField(default=True),
        ),
    ]