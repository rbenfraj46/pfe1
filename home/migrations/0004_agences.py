# Generated by Django 3.2.11 on 2022-01-26 16:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_alter_user_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agency_name', models.CharField(max_length=4096, verbose_name='Agency Name')),
                ('ceo_name', models.CharField(max_length=150, verbose_name='CEO Name')),
                ('tax_number', models.CharField(max_length=150, verbose_name='Tax registration Number')),
                ('adress_agency', models.CharField(max_length=4096, verbose_name='Adress')),
                ('governorate', models.CharField(max_length=200, verbose_name='Governorate')),
                ('city', models.CharField(max_length=200, verbose_name='City')),
                ('email', models.EmailField(max_length=255, null=False, unique=True, verbose_name='email address')),
                ('phone_number', models.CharField(max_length=200, verbose_name='Phone')),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('update_date', models.DateField(auto_now=True)),
                ('is_mail_verified', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
            ],
            options={
                'db_table': 'agence',
            },
        ),
    ]
