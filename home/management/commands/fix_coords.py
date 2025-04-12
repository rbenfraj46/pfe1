from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from home.models import Agences

class Command(BaseCommand):
    help = 'Corriger les coordonnées de l\'agence en les définissant en WGS84'

    def handle(self, *args, **options):
        self.stdout.write('Début de la correction des coordonnées...')
        
        for agence in Agences.objects.all():
            # Définir les coordonnées pour Kairouan, Tunisie
            agence.location = Point(10.590820312500002, 36.49887343713957, srid=4326)
            agence.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Agence {agence.agency_name} mise à jour avec les coordonnées: {agence.location}'
                )
            )