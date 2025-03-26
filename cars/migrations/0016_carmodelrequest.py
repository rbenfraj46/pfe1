# Generated by Django 3.2.11 on 2025-03-23 12:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0020_auto_20250319_0801'),
        ('cars', '0015_carunavailability'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarModelRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Model Name')),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('admin_notes', models.TextField(blank=True, null=True)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cars.brand')),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.agences')),
            ],
            options={
                'db_table': 'car_model_request',
            },
        ),
    ]
