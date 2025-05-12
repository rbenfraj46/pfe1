from django.db import migrations

def add_initial_currencies(apps, schema_editor):
    Devise = apps.get_model('home', 'Devise')
    currencies = [
        {
            'name': 'TND',
            'description': 'Dinar Tunisien',
            'value': 1.0,
            'coefficient': 1.0,
            'is_active': True,
            'order_key': 1,
            'unit': 1
        },
        {
            'name': 'EUR',
            'description': 'Euro',
            'value': 3.35,
            'coefficient': 1.0,
            'is_active': True,
            'order_key': 2,
            'unit': 1
        },
        {
            'name': 'USD',
            'description': 'Dollar Américain',
            'value': 3.08,
            'coefficient': 1.0,
            'is_active': True,
            'order_key': 3,
            'unit': 1
        }
    ]
    
    for currency in currencies:
        Devise.objects.create(**currency)

def remove_currencies(apps, schema_editor):
    Devise = apps.get_model('home', 'Devise')
    Devise.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_initial_currencies, remove_currencies),
    ]