from django.db import migrations

USER_NAME = "admin"
PASSWD = "$Agem001"
EMAIL = "admin@admin.org"

def load_data(apps, schema_editor):
    User = apps.get_model('home', 'User')
    User.objects.create_user(username=USER_NAME, password=PASSWD,
                             email=EMAIL, is_mail_verified=True,
                             is_staff=True, is_superuser=True,
                             first_name="Administrator", last_name="User")



class Migration(migrations.Migration):

    dependencies = [
        ('home', 'tunisia_cities_creations'),
    ]

    operations = [
        migrations.RunPython(load_data)
    ]

