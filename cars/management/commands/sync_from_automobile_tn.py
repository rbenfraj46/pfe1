import logging
import re

from django.core.management.base import BaseCommand
from django.conf import settings

from cars.utils import automobile_tn
from cars.models import Brand
from cars.models import CarModel


class Command(BaseCommand):
    help = "Update brands and cars from https://automobile.tn ."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry',
            action='store_true',
            help='Simulate sync only do not update Anything',
        )

        parser.add_argument(
            '--brand',
            action='store',
            dest='brand',
            default='',
            #choices=Devise.objects.filter(is_active=True).values_list('name', flat=True),
            help='Update specific brand example audi',
        )

    def handle(self, *args, **options):
        store = True
        verbosity = int(options['verbosity'])
        root_logger = logging.getLogger('')
        if verbosity == 0:
            root_logger.setLevel(logging.ERROR)
        elif verbosity == 1:
            root_logger.setLevel(logging.INFO)
        elif verbosity > 1:
            root_logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        root_formatter = logging.Formatter('%(levelname)-7s - %(filename)-26s:%(lineno)-3d - ' +
                                           '%(asctime)s: %(message)s')
        handler.setFormatter(root_formatter)
        root_logger.addHandler(handler)

        if options['dry']:
            root_logger.info('This is only simulation. Nothing will not be affected.')
            store = False

        update_brand(store, options['brand'], root_logger)


def update_brand(store, given_brand, logger):
    """ update car brand """

    car_brands = automobile_tn.get_brand_dict()

    for brand, details in car_brands.items():
        if given_brand and brand != given_brand:
            logger.debug("Ignore brand %s", brand)
            continue

        db_brand = Brand.objects.filter(name__iexact=brand).first()
        if db_brand:
            logger.info('Ignoring brand %s since it exists locally.', brand)
        else:
            img_url = details['img_url'].split('?')[0]
            img_name = img_url.split('/')[-1]
            img_hash, img_ext = automobile_tn.get_name_extension(img_name)
            db_brand = Brand()
            db_brand.name = capitalize_string(brand)
            db_brand.img_hash = img_hash + "." + img_ext
            db_brand.img_extension = img_ext
            if store:
                if settings.AUTOMOBILE_TN_DOWNLOAD_IMAGES:
                    # save brand into DB
                    logger.debug('Downloading %s', img_url)
                    automobile_tn.download_images(img_url, img_hash + "." + img_ext)
                db_brand.save()
                logger.debug('Saving brand %s', capitalize_string(brand))
            else:
                logger.info('In Store mode. brand %s will be saved to the Database.', capitalize_string(brand))
                if settings.AUTOMOBILE_TN_DOWNLOAD_IMAGES:
                    logger.info('This is simulating mode. In store mode: %s will be downloaded.', img_url)
        update_cars(store, brand, logger, db_brand, details['url'])


def capitalize_string(string_field):
    result = string_field.lower()
    for separator in [' ', '-', '_']:
        result = separator.join([x[0].upper()+x[1:] for x in result.split(separator)])
    return result

def update_cars(store, brand, logger, db_brand, brand_url):
    """ update car of the given brand """
    #import pprint
    cars_dict = automobile_tn.get_cars_by_brand(brand_url)
    #pprint.pprint(cars_dict)
    for car, details in cars_dict.items():
        cars_infos = automobile_tn.get_cars_infos(details['url'])
        for car_name, car_infos in cars_infos.items():
            #pprint.pprint(car_infos)
            db_car = CarModel.objects.filter(name__iexact=car_name.strip()).first()
            if db_car:
                logger.info('Ignoring Car Model %s since it exists locally.', car_name)
                continue

            if not store:
                logger.info('In store mode model version "%s" will be saved.', car_name)
            else:
                if not db_car:
                    db_car = CarModel()
                    db_car.name = car_name.strip()

                img_url = car_infos['img_url'].split('?')[0]
                img_name = img_url.split('/')[-1]
                img_hash, img_extension = automobile_tn.get_name_extension(img_name)

                if settings.AUTOMOBILE_TN_DOWNLOAD_IMAGES:
                    # save car image into DB
                    logger.info('Downloading %s', img_url)
                    automobile_tn.download_images(img_url, img_hash + "." + img_extension, db_brand.name)

                db_car.img_hash, db_car.img_extension = img_hash + "." + img_extension, img_extension
                db_car.brand = db_brand
                db_car.air_conditioner = car_infos['air_conditioner']
                db_car.category = car_infos['category']
                # cynlinder per litre:
                # extract 1498 CM³ -> 1.498
                db_car.cylinder = float(extract_from_regex(car_infos['cylinder'], r"(\d*) CM³", logger)/1000)
                # "horse_power": "8 CV",
                db_car.horse_power = float(extract_from_regex(car_infos['horse_power'], r"(\d*) CV", logger))
                db_car.doors_nbr = int_or_none(car_infos['doors_nbr'])
                db_car.place_nbr = int_or_none(car_infos['place_nbr'])
                db_car.energy = car_infos['energy']
                # "extra_urban_consumption": "5.1 L/100 km",
                db_car.extra_urban_consumption = float(extract_from_regex(car_infos['extra_urban_consumption'], r"(\d*?.\d*) L/100 km", logger))
                db_car.urban_consumption = float(extract_from_regex(car_infos['urban_consumption'], r"(\d*?.\d*) L/100 km", logger))
                db_car.mixte_consumption = float(extract_from_regex(car_infos['mixte_consumption'], r"(\d*?.\d*) L/100 km", logger))
                db_car.gear_type = car_infos['gear_type']
                db_car.gear_nbr = int_or_none(car_infos['gear_nbr'])
                db_car.transmission = car_infos['transmission']
                # "max_speed": "207 KM/H",
                db_car.max_speed = int(extract_from_regex(car_infos['max_speed'], r"(\d*) KM/H", logger))

                # "length": "4484 mm",
                db_car.length = float(extract_from_regex(car_infos['length'], r"(\d*) mm", logger)/1000)
                db_car.width = float(extract_from_regex(car_infos['width'], r"(\d*) mm", logger)/1000)
                db_car.height = float(extract_from_regex(car_infos['height'], r"(\d*) mm", logger)/1000)

                # "trunk_volume": "530 L",
                db_car.trunk_volume = int(extract_from_regex(car_infos['trunk_volume'], r"(\d*) L", logger))

                db_car.save()
                logger.info('Saving Car Model %s', db_car.name)


def extract_from_regex(content, regex, logger):
    result = 0
    try:
        res = re.findall(regex, content)
        if res:
            result = float(res[0])
    except Exception as exp:
        logger.error("Exception occured: %s\n While extraction %s from %s", exp, regex, content)
    return result

def int_or_none(value):
    try:
        return int(value)
    except ValueError:
        return None


