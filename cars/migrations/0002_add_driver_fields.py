from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='agencycar',
            name='with_driver',
            field=models.BooleanField(default=False, verbose_name='With Driver'),
        ),
        migrations.AddField(
            model_name='agencycar',
            name='driver_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Driver Name'),
        ),
        migrations.AddField(
            model_name='agencycar',
            name='driver_phone',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Driver Phone'),
        ),
        migrations.AddField(
            model_name='agencycar',
            name='driver_license_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Driver License Number'),
        ),
        migrations.AddField(
            model_name='agencycar',
            name='driver_experience_years',
            field=models.IntegerField(blank=True, null=True, verbose_name='Driver Experience (Years)'),
        ),
        migrations.AddField(
            model_name='agencycar',
            name='driver_languages',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Driver Languages'),
        ),
    ]