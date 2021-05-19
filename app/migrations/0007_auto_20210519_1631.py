# Generated by Django 3.2.3 on 2021-05-19 19:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_remove_venta_num_vta'),
    ]

    operations = [
        migrations.AddField(
            model_name='personal',
            name='farmacia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.farmacia'),
        ),
        migrations.AddField(
            model_name='venta',
            name='farmacia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.farmacia'),
        ),
    ]
