# Generated by Django 3.2.11 on 2025-03-23 12:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0020_auto_20250319_0801'),
        ('cars', '0016_carmodelrequest'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='carmodelrequest',
            options={'verbose_name': 'Car Model Request', 'verbose_name_plural': 'Car Model Requests'},
        ),
        migrations.AlterField(
            model_name='carmodelrequest',
            name='brand',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='cars.brand'),
        ),
        migrations.AlterField(
            model_name='carmodelrequest',
            name='requested_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.agences'),
        ),
    ]
