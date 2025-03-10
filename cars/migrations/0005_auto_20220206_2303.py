# Generated by Django 3.2.11 on 2022-02-06 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0004_auto_20220205_2226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carmodel',
            name='height',
            field=models.FloatField(blank=True, null=True, verbose_name='Car Height'),
        ),
        migrations.AlterField(
            model_name='carmodel',
            name='length',
            field=models.FloatField(blank=True, null=True, verbose_name='Car Length'),
        ),
        migrations.AlterField(
            model_name='carmodel',
            name='width',
            field=models.FloatField(blank=True, null=True, verbose_name='Car Width'),
        ),
    ]
