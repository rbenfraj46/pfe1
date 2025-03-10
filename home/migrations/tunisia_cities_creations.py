from django.db import migrations, transaction
import json
from django.contrib.gis.geos import fromstr
from pathlib import Path

DATA_FILENAME = 'utils/city_json/tunisia_cities_exported.json'


def load_data(apps, schema_editor):
    State = apps.get_model('home', 'State')
    Delegation = apps.get_model('home', 'Delegation')
    City = apps.get_model('home', 'City')
    jsonfile = Path(__file__).parents[2] / DATA_FILENAME

    with transaction.atomic():
        with open(str(jsonfile)) as datafile:
            countries = json.load(datafile)
            for name, country in countries.items():
                longitude = country.get('lon', 0)
                latitude = country.get('lat', 0)
                location = fromstr(
                    f'POINT({longitude} {latitude})', srid=4326
                )
                state = State(name=name, position=location)
                state.save()
                # loop over delegations
                for _name, delegations in country.items():
                    if _name in ('lon', 'lat'):
                        continue
                    longitude = delegations.get('lon', 0)
                    latitude = delegations.get('lat', 0)
                    location = fromstr(
                        f'POINT({longitude} {latitude})', srid=4326
                    )
                    delegation = Delegation(name=_name, position=location)
                    delegation.save()
                    delegation.state = state
                    delegation.save()

                    # loop over cities
                    for locality in delegations['delegation'][0]["locality"]:
                        longitude = locality.get('lon', 0)
                        latitude = locality.get('lat', 0)
                        location = fromstr(
                            f'POINT({longitude} {latitude})', srid=4326
                        )
                        zipcode = locality.get('zipcode', 0)
                        loc_name = locality.get('name', "No Name Given")
                        city = City(name=loc_name, position=location, zipcode=zipcode)
                        city.save()
                        city.delegation = delegation
                        city.save()


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_auto_20220126_1402'),
    ]

    operations = [
        migrations.RunPython(load_data)
    ]

