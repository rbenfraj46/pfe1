import logging
import requests
import json
import urllib3

from django.conf import settings
from django.core.management.base import BaseCommand

from home.models import Devise

urllib3.disable_warnings()

proxyDict = {
              "http"  : settings.HTTP_PROXY,
              "https" : settings.HTTP_PROXY,
              "ftp"   : settings.HTTP_PROXY
            }


VERSION = '1.0.0'

class Command(BaseCommand):
    help = "Update currency."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry',
            action='store_true',
            help='Simulate sync only do not update Database',
        )

        parser.add_argument(
            '--currency',
            action='store',
            dest='currency',
            default='',
            #choices=Devise.objects.filter(is_active=True).values_list('name', flat=True),
            help='Update specific currency',
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
        root_formatter = logging.Formatter('%(levelname)s - %(filename)s:%(lineno)d - ' +
                                           '%(asctime)s: %(msg)s')
        handler.setFormatter(root_formatter)
        root_logger.addHandler(handler)

        if options['dry']:
            root_logger.info('This is only simulation. Database will not be affected.')
            store = False

        update_currency(store, options['currency'], root_logger)


def update_currency(store, currency, logger):
    ALL_AVAILABLE_CURRENCY = False
    if currency and currency.upper() != "ALL":
        currencies = Devise.objects.filter(is_active=True).filter(name=currency.upper()).all()
        if not currencies:
            logger.error('No such currency "%s"' % currency)
            exit(1)

    else:
        currencies = Devise.objects.filter(is_active=True).all()

    if currency.upper() == "ALL":
        ALL_AVAILABLE_CURRENCY = True

    currency_change = {}
    try:
        url = "https://freecurrencyapi.net/api/v2/latest?apikey=%s&base_currency=%s" % (settings.FREECURRENCYAPI_TOKEN, settings.DEFAULT_CURRENCY)
        response = requests.get(url, proxies=proxyDict)
        if response.status_code == 200:
            data = json.loads(response.content)
            currency_change = data['data']
    except Exception as exp:
        logger.error('Exception occured while retrieving currency:\n', str(exp))

    for currency in currencies:
        if currency.name == settings.DEFAULT_CURRENCY:
            continue

        if currency.name not in currency_change:
            logger.error('Could not retrieve currency %s' % currency.name)
            continue

        value = currency_change[currency.name]
        if store:
            logger.info('Update Currency %s with value %s' % (currency.name, value))
            currency.value = value
            currency.save()
        else:
            logger.info('This is dry mode: in store mode Currency %s will be updated with value %s' % (currency.name, value))

    if ALL_AVAILABLE_CURRENCY:
        # add missing_currencies:
        currencies = list(Devise.objects.values_list('name', flat=True))

        for name, value in currency_change.items():
            devise = None
            if name.upper() in currencies:
                devise = Devise.objects.get(name=name.upper())
                if store:
                    logger.info('Updating inactive Currency %s with value %s' % (name, value))
                else:
                    logger.info('In store mode Inactive Currency %s with value %s will be updated' % (name, value))

            else:
                devise = Devise()
                devise.name = name.upper()
                devise.description = name.upper()
                devise.is_active = False
                devise.coefficient = 1
                devise.value = value
                if store:
                    logger.info('Add missing Currency %s with value %s as inactive' % (name, value))
                else:
                    logger.info('In store mode Missing Currency %s with value %s will be added as inactive' % (name, value))

            if store:
                devise.save()


