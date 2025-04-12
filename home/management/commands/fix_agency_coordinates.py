from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from math import pi, log, tan, atan, exp
from home.models import Agences

class Command(BaseCommand):
    help = 'Corriger les coordonnées des agences en les convertissant en WGS84'

    def merc_to_lat(self, y):
        return atan(exp(y / 6378137.0)) * 360.0 / pi - 90.0

    def handle(self, *args, **options):
        self.stdout.write('Début de la correction des coordonnées...')
        
        for agence in Agences.objects.all():
            if agence.location:
                try:
                    # Coordonnées Web Mercator originales
                    x, y = agence.location.coords
                    
                    # Conversion de Web Mercator vers WGS84
                    lon = x * 180.0 / 20037508.34
                    lat = self.merc_to_lat(y)
                    
                    # Vérifier que les coordonnées sont valides
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        # Créer un nouveau point en WGS84
                        agence.location = Point(lon, lat, srid=4326)
                        agence.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Agence {agence.agency_name} mise à jour: {agence.location}'
                            )
                        )
                    else:
                        # Si les coordonnées sont invalides, définir un point par défaut pour la Tunisie
                        agence.location = Point(10.181667, 36.806389, srid=4326)  # Tunis
                        agence.save()
                        self.stdout.write(
                            self.style.WARNING(
                                f'Coordonnées invalides pour {agence.agency_name}, utilisation des coordonnées par défaut'
                            )
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Erreur lors de la mise à jour de {agence.agency_name}: {str(e)}'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Agence {agence.agency_name} n\'a pas de localisation'
                    )
                )