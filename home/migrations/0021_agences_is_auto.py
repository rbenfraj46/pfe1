# Generated by Django 3.2.11 on 2025-03-30 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0020_auto_20250319_0801'),
    ]

    operations = [
        migrations.AddField(
            model_name='agences',
            name='is_auto',
            field=models.BooleanField(default=False, verbose_name='Auto Activate Cars'),
        ),
    ]
