# Generated by Django 3.2.3 on 2021-05-16 00:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_venta_metodo_pago'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='venta',
            name='num_vta',
        ),
    ]
