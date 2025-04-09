# Generated by Django 3.2.11 on 2025-04-08 18:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0021_agences_is_auto'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgencyUserPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission', models.CharField(choices=[('view_cars', 'View Cars'), ('add_cars', 'Add Cars'), ('edit_cars', 'Edit Cars'), ('delete_cars', 'Delete Cars')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_permissions', to='home.agences')),
                ('granted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='granted_permissions', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_permissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Agency User Permission',
                'verbose_name_plural': 'Agency User Permissions',
                'db_table': 'agency_user_permission',
            },
        ),
        migrations.AddIndex(
            model_name='agencyuserpermission',
            index=models.Index(fields=['agency', 'user', 'permission'], name='agency_user_agency__a3d88b_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='agencyuserpermission',
            unique_together={('agency', 'user', 'permission')},
        ),
    ]
