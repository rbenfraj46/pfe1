# Generated by Django 3.2.11 on 2022-02-17 00:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_alter_mailsubscription_subscription_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='has_newsletter_subscription',
        ),
        migrations.AlterField(
            model_name='mailsubscription',
            name='unsubscription_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='UnSubscripted At'),
        ),
    ]
