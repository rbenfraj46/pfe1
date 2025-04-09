# Generated by Django 3.2.11 on 2025-04-08 19:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0023_delete_agencyuserpermission'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgencyPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission', models.CharField(choices=[('view', 'View Cars'), ('add', 'Add Cars'), ('edit', 'Edit Cars'), ('delete', 'Delete Cars')], max_length=20)),
                ('granted_at', models.DateTimeField(auto_now_add=True)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.agences')),
                ('granted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='granted_permissions', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'agency_permission',
                'unique_together': {('agency', 'user', 'permission')},
            },
        ),
    ]
