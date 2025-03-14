# Generated by Django 3.2.11 on 2022-03-20 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_auto_20220319_2102'),
    ]

    operations = [
        migrations.AddField(
            model_name='agences',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='logo'),
        ),
        migrations.AlterField(
            model_name='agences',
            name='tax_number',
            field=models.CharField(max_length=150, unique=True, verbose_name='Tax registration Number'),
        ),
    ]
