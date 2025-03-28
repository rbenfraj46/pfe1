# Generated by Django 3.2.11 on 2025-03-23 08:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0014_alter_agencycar_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarUnavailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(verbose_name='Start Date')),
                ('end_date', models.DateField(verbose_name='End Date')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unavailability_periods', to='cars.agencycar')),
            ],
            options={
                'verbose_name': 'Car Unavailability',
                'verbose_name_plural': 'Car Unavailability',
                'db_table': 'car_unavailability',
            },
        ),
    ]
