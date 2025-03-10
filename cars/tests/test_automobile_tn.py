import sys
import os
import json

from io import StringIO

from django.test import TestCase
from django.core.management import call_command
from django.utils import timezone


from django.conf import settings

import responses
import pathlib

from cars.utils import automobile_tn
from cars.models import CarModel

FIXTURE_PATH = str(pathlib.Path(__file__).parent.resolve()) + "/fixtures/"


class SyncAutomobileTnCommand(TestCase):
    maxDiff = None
    SIMULATION_MSG = "This is only simulation. Nothing will not be affected."
    settings.AUTOMOBILE_TN_DOWNLOAD_IMAGES = True
    automobile_tn.BRAND_IMAGE_FOLDER = "tmp_download/"

    def tearDown(self):
        os.system("rm -fr %s" % automobile_tn.BRAND_IMAGE_FOLDER)
        settings.AUTOMOBILE_TN_DOWNLOAD_IMAGES = True
        TestCase.tearDown(self)

    def test_get_infos_multiple(self):

        with open(FIXTURE_PATH + 'multiple_version.html', 'r') as file:
            data = file.read().rstrip()

        responses.add(
            responses.Response(method='GET',
                               url="https://www.automobile.tn/fr/neuf/audi/q3",
                               body=data,
                               status=200))

        with open(FIXTURE_PATH + 'multiple_version_first.html', 'r') as file:
            data = file.read().rstrip()

        responses.add(
            responses.Response(method='GET',
                               url="https://www.automobile.tn/fr/neuf/audi/q3/35-tfsi-advanced",
                               body=data,
                               status=200))

        with open(FIXTURE_PATH + 'multiple_version_second.html', 'r') as file:
            data = file.read().rstrip()

        responses.add(
            responses.Response(method='GET',
                               url="https://www.automobile.tn/fr/neuf/audi/q3/35-tfsi-s-tronic-advanced-plus",
                               body=data,
                               status=200))
        result = automobile_tn.get_cars_infos("https://www.automobile.tn/fr/neuf/audi/q3")
        with open(FIXTURE_PATH + 'multiple_version.json', 'r') as file:
            data = file.read().rstrip()
            self.assertEqual(result, json.loads(data))

    def test_get_infos_simple(self):
        with open(FIXTURE_PATH + 'simple_version.html', 'r') as file:
            data = file.read().rstrip()

        responses.add(
            responses.Response(method='GET',
                               url="https://www.automobile.tn/fr/neuf/hyundai/grand-i10-populaire/1.0-l",
                               body=data,
                               status=200))

        result = automobile_tn.get_cars_infos("https://www.automobile.tn/fr/neuf/hyundai/grand-i10-populaire/1.0-l")
        self.assertEqual(result, {
            "Hyundai Grand i10 Populaire 1.0 L ": {
                "img_url": "https://catalogue.automobile.tn/big/2021/01/46490.jpg?t=1643889681",
                "place_nbr": "5",
                "category": "Citadine",
                "doors_nbr": "5",
                "energy": "Essence",
                "horse_power": "4 CV",
                "cylinder": "998 CM³",
                "gear_type": "Manuelle",
                "gear_nbr": "5",
                "length": "3805 mm",
                "width": "1680 mm",
                "height": "1510 mm",
                "trunk_volume": "260 L",
                "max_speed": "161 KM/H",
                "urban_consumption": "6.5 L/100 km",
                "extra_urban_consumption": "4.1 L/100 km",
                "mixte_consumption": "5 L/100 km",
                "air_conditioner": "Manuelle",
                "roof": "",
                "transmission": "Traction"
            }
        })

    def call_command(self, *args, **kwargs):
        out = StringIO()
        _stderr = StringIO()
        sys.stdout = out
        sys.stderr = _stderr
        call_command(
            "sync_from_automobile_tn",
            *args,
            stdout=out,
            stderr=_stderr,
            **kwargs,
        )
        return out.getvalue() + _stderr.getvalue()

    def test_dry_run_audi_brand(self):
        with open(FIXTURE_PATH + 'neuf.html', 'r') as file:
            data = file.read().rstrip()
        responses.add(
            responses.Response(method='GET',url=settings.AUTOMOBILE_TN_URL,
                               body=data,
                               status=200))
        with open(FIXTURE_PATH + 'audi.html', 'r') as file:
            data_audi = file.read().rstrip()
        responses.add(
            responses.Response(method='GET',url=settings.AUTOMOBILE_TN_URL+"/audi",
                               body=data_audi,
                               status=200))

        with open(FIXTURE_PATH + 'multiple_version.html', 'r') as file:
            data_audi = file.read().rstrip()
        responses.add(
            responses.Response(method='GET',url=settings.AUTOMOBILE_TN_URL+"/audi/q3",
                               body=data_audi,
                               status=200))

        with open(FIXTURE_PATH + 'multiple_version_first.html', 'r') as file:
            data_audi = file.read().rstrip()
        responses.add(
            responses.Response(method='GET',url=settings.AUTOMOBILE_TN_URL+"/audi/q3/35-tfsi-advanced",
                               body=data_audi,
                               status=200))

        with open(FIXTURE_PATH + 'multiple_version_second.html', 'r') as file:
            data_audi = file.read().rstrip()
        responses.add(
            responses.Response(method='GET',url=settings.AUTOMOBILE_TN_URL+"/audi/q3/35-tfsi-s-tronic-advanced-plus",
                               body=data_audi,
                               status=200))

        before_command = timezone.now()
        cars = CarModel.objects.filter(updated__gte=before_command)
        self.assertEqual(len(cars), 0)
        out = self.call_command("--dry",  "--brand", "audi")
        cars = CarModel.objects.filter(updated__gte=before_command)
        self.assertEqual(len(cars), 0)
        self.assertIn(self.SIMULATION_MSG, out)
        self.assertIn("In Store mode. brand Audi will be saved to the Database.", out)
        self.assertIn("This is simulating mode. In store mode: https://catalogue.automobile.tn/marques/2.png will be downloaded.", out)
        self.assertIn('In store mode model version "Audi Q3 35 TFSI S-tronic Advanced" will be saved.', out)
        self.assertIn('In store mode model version "Audi Q3 35 TFSI S-tronic Advanced Plus" will be saved.', out)

    def test_run_audi_brand_without_images(self):
        settings.AUTOMOBILE_TN_DOWNLOAD_IMAGES = False
        with open(FIXTURE_PATH + 'neuf.html', 'r') as file:
            data = file.read().rstrip()
        responses.add(
            responses.Response(method='GET',url=settings.AUTOMOBILE_TN_URL,
                               body=data,
                               status=200))
        with open(FIXTURE_PATH + 'audi.html', 'r') as file:
            data_audi = file.read().rstrip()
        responses.add(
            responses.Response(method='GET',url=settings.AUTOMOBILE_TN_URL+"/audi",
                               body=data_audi,
                               status=200))

        with open(FIXTURE_PATH + 'multiple_version.html', 'r') as file:
            data_audi = file.read().rstrip()
        responses.add(
            responses.Response(method='GET',url=settings.AUTOMOBILE_TN_URL+"/audi/q3",
                               body=data_audi,
                               status=200))

        with open(FIXTURE_PATH + 'multiple_version_first.html', 'r') as file:
            data_audi = file.read().rstrip()
        responses.add(
            responses.Response(method='GET',url=settings.AUTOMOBILE_TN_URL+"/audi/q3/35-tfsi-advanced",
                               body=data_audi,
                               status=200))

        with open(FIXTURE_PATH + 'multiple_version_second.html', 'r') as file:
            data_audi = file.read().rstrip()
        responses.add(
            responses.Response(method='GET',url=settings.AUTOMOBILE_TN_URL+"/audi/q3/35-tfsi-s-tronic-advanced-plus",
                               body=data_audi,
                               status=200))

        before_command = timezone.now()
        cars = CarModel.objects.filter(updated__gte=before_command)
        self.assertEqual(len(cars), 0)
        out = self.call_command("--brand", "audi")
        cars = CarModel.objects.filter(updated__gte=before_command)
        self.assertEqual(len(cars), 2)
        self.assertIn("Saving brand Audi", out)
        self.assertIn('Saving Car Model Audi Q3 35 TFSI S-tronic Advanced', out)
        self.assertIn('Saving Car Model Audi Q3 35 TFSI S-tronic Advanced Plus', out)

    def test_run_audi_brand_with_images(self):
        settings.AUTOMOBILE_TN_DOWNLOAD_IMAGES = True

        with open(FIXTURE_PATH + 'neuf.html', 'r') as file:
            data = file.read().rstrip()
        responses.add(
            responses.Response(method='GET',url=settings.AUTOMOBILE_TN_URL,
                               body=data,
                               status=200))
        with open(FIXTURE_PATH + 'audi.html', 'r') as file:
            data_audi = file.read().rstrip()
        responses.add(
            responses.Response(method='GET',url=settings.AUTOMOBILE_TN_URL+"/audi",
                               body=data_audi,
                               status=200))

        with open(FIXTURE_PATH + 'multiple_version.html', 'r') as file:
            data_audi = file.read().rstrip()
        responses.add(
            responses.Response(method='GET',url=settings.AUTOMOBILE_TN_URL+"/audi/q3",
                               body=data_audi,
                               status=200))

        with open(FIXTURE_PATH + 'multiple_version_first.html', 'r') as file:
            data_audi = file.read().rstrip()
        responses.add(
            responses.Response(method='GET',url=settings.AUTOMOBILE_TN_URL+"/audi/q3/35-tfsi-advanced",
                               body=data_audi,
                               status=200))

        with open(FIXTURE_PATH + 'multiple_version_second.html', 'r') as file:
            data_audi = file.read().rstrip()
        responses.add(
            responses.Response(method='GET',url=settings.AUTOMOBILE_TN_URL+"/audi/q3/35-tfsi-s-tronic-advanced-plus",
                               body=data_audi,
                               status=200))

        with open(FIXTURE_PATH + '2.png', 'rb') as file:
            data_audi = file.read()
        responses.add(
            responses.Response(method='GET',url="https://catalogue.automobile.tn/marques/2.png",
                               body=data_audi,
                               status=200))

        with open(FIXTURE_PATH + '46244.jpg', 'rb') as file:
            data_audi = file.read()
        responses.add(
            responses.Response(method='GET',url="https://catalogue.automobile.tn/big/2019/09/46244.jpg",
                               body=data_audi,
                               status=200))

        with open(FIXTURE_PATH + '46488.jpg', 'rb') as file:
            data_audi = file.read()
        responses.add(
            responses.Response(method='GET',url="https://catalogue.automobile.tn/big/2021/01/46488.jpg",
                               body=data_audi,
                               status=200))

        before_command = timezone.now()
        cars = CarModel.objects.filter(updated__gte=before_command)
        self.assertEqual(len(cars), 0)
        out = self.call_command("--brand", "audi")
        cars = CarModel.objects.filter(updated__gte=before_command)
        self.assertEqual(len(cars), 2)
        self.assertIn("Saving brand Audi", out)
        self.assertIn('Saving Car Model Audi Q3 35 TFSI S-tronic Advanced', out)
        self.assertIn('Saving Car Model Audi Q3 35 TFSI S-tronic Advanced Plus', out)
        self.assertIn('Downloading https://catalogue.automobile.tn/big/2019/09/46244.jpg', out)
        self.assertIn('Downloading https://catalogue.automobile.tn/big/2021/01/46488.jpg', out)


