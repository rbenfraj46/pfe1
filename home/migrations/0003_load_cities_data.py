from django.db import migrations
from django.contrib.gis.geos import Point
import json

def load_cities_data(apps, schema_editor):
    State = apps.get_model('home', 'State')
    Delegation = apps.get_model('home', 'Delegation')
    City = apps.get_model('home', 'City')

    # Charger le fichier JSON
    with open('utils/city_json/tunisia_cities_exported.json', 'r') as f:
        data = json.load(f)

    # Parcourir les données et les insérer
    for state_name, state_data in data.items():
        # Créer l'état
        state = State.objects.create(
            name=state_name,
            position=Point(float(state_data['lon']), float(state_data['lat']), srid=4326)
        )

        # Parcourir les délégations
        for deleg_name, deleg_data in {k:v for k,v in state_data.items() if k not in ['lat', 'lon']}.items():
            # Créer la délégation
            delegation = Delegation.objects.create(
                name=deleg_name,
                state=state,
                position=Point(float(deleg_data['lon']), float(deleg_data['lat']), srid=4326)
            )

            # Parcourir les localités
            for deleg_info in deleg_data.get('delegation', []):
                for locality in deleg_info.get('locality', []):
                    if 'lon' in locality:
                        # Créer la ville
                        City.objects.create(
                            name=deleg_name,  # Utiliser le nom de la délégation comme nom de ville
                            delegation=delegation,
                            position=Point(float(locality['lon']), float(deleg_data['lat']), srid=4326)
                        )

class Migration(migrations.Migration):
    dependencies = [
        ('home', '0002_add_initial_currencies'),
    ]

    operations = [
        migrations.RunPython(load_cities_data),
    ]