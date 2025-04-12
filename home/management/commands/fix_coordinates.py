from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from home.models import Agences
from django.contrib.gis.gdal import SpatialReference, CoordTransform

class Command(BaseCommand):
    help = 'Corriger les coordonnées des agences en les transformant en WGS84 (SRID 4326)'

    def handle(self, *args, **kwargs):
        for agence in Agences.objects.all():
            if agence.location:
                # Si le point est dans un autre système de coordonnées, le convertir en WGS84
                if agence.location.srid != 4326:
                    # Créer la transformation du système source vers WGS84
                    source_srid = agence.location.srid
                    source_srs = SpatialReference(source_srid)
                    target_srs = SpatialReference(4326)
                    transform = CoordTransform(source_srs, target_srs)
                    
                    # Appliquer la transformation
                    agence.location.transform(transform)
                    agence.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Coordonnées corrigées pour {agence.agency_name}: {agence.location}'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Aucune localisation pour {agence.agency_name}'
                    )
                )