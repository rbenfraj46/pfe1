from django.db import migrations, transaction

def create_milestone_names(apps, schema_editor):
    Devise = apps.get_model('home', 'Devise')
    with transaction.atomic():
        order = 1
        for name in ('TND', 'USD', 'EUR', 'GBP'):
            devise = Devise()
            devise.name = name
            devise.value = 1
            devise.description = name
            devise.is_active = True
            devise.order_key = order
            devise.save()
            order = order + 1

class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('home', '0005_auto_20220124_2117'),
    ]

    operations = [
        migrations.RunPython(create_milestone_names),
    ]
