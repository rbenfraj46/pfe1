# Generated by Django 3.2.11 on 2025-05-13 07:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transfervehicle',
            name='agence',
        ),
        migrations.RemoveField(
            model_name='transfervehicle',
            name='brand',
        ),
        migrations.DeleteModel(
            name='TransferBooking',
        ),
        migrations.DeleteModel(
            name='TransferVehicle',
        ),
    ]
