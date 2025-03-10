import os
import requests
import hashlib
import logging
import urllib3
import pprint

from django.conf import settings

from bs4 import BeautifulSoup


proxyDict = {
              "http"  : settings.HTTP_PROXY,
              "https" : settings.HTTP_PROXY,
              "ftp"   : settings.HTTP_PROXY
            }

headersDict = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Accept': 'text/html, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }

CAR_FIELD = {'Nombre de places': 'place_nbr',
             'Carrosserie': 'category',
             'Nombre de portes': 'doors_nbr',
             'Energie ': 'energy',
             'Puissance fiscale': 'horse_power',
             'Cylindrée': 'cylinder',
             'Boîte': 'gear_type',
             'Nombre de rapports': 'gear_nbr',
             'Longueur ': 'length',
             'Largeur': 'width',
             'Hauteur': 'height',
             'Volume du coffre': 'trunk_volume',
             'Vitesse maxi': 'max_speed',
             'Consommation urbaine ': 'urban_consumption',
             'Consommation extra-urbaine': 'extra_urban_consumption',
             'Consommation mixte ': 'mixte_consumption',
             'Climatisation': 'air_conditioner',
             'Toit': 'roof',
             'Transmission': 'transmission',
             }


logger = logging.getLogger('')
urllib3.disable_warnings()

#DOWNLOAD_FOLDER = settings.MEDIA_ROOT + settings.CAR_DOWNLOAD_FOLDER
BRAND_IMAGE_FOLDER = settings.MEDIA_ROOT + settings.CAR_DOWNLOAD_FOLDER


def get_brand_dict():
    data = {}
    response = requests.get(settings.AUTOMOBILE_TN_URL, proxies=proxyDict, headers=headersDict)
    soup = BeautifulSoup(response.text, 'html.parser')
    #print(soup.find_all(class_='container'))
    brands = soup.find_all(class_='container')[0].find_all('a')

    for brand in brands:
        url = brand.get('href')
        if len(url.split('/')) != 4:
            continue
        data[url.split('/')[3]] = {'url': settings.AUTOMOBILE_TN_BASE_URL + url,
                                   'img_url': brand.picture.img.get('src')}
    return data


def get_name_extension(name):
    file_name = ''.join(name.split('.')[:-1])
    extension = ''
    if len(name.split('.')) > 1:
        extension = name.split('.')[-1]
    file_name = hashlib.md5(file_name.encode()).hexdigest()
    return file_name, extension


def download_images(url, name, brand=''):
    response = requests.get(url, proxies=proxyDict, headers=headersDict)
    destination_folder = BRAND_IMAGE_FOLDER + '/' + brand
    if response.status_code == 200:
        if not os.path.isdir(destination_folder):
            logger.info('Creating folder: %s', destination_folder)
            os.makedirs(destination_folder)

        # save image folder
        try:
            image_path = destination_folder + "/" + name
            if os.path.isfile(image_path):
                logger.debug("File %s already exists!!", image_path)
                return
            with open(image_path, 'wb') as f:
                f.write(response.content)
        except Exception as exp:
            logger.error('Error occured while downloading: \n%s\n%s', url, str(exp))


def get_cars_by_brand(brand_url):
    response = requests.get(brand_url, proxies=proxyDict, headers=headersDict)
    data = {}
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        cars = soup.find_all(class_='articles')[0].find_all('a')

        for car in cars:
            url = car.get('href')
            if len(url.split('/')) < 5:
                logger.warning("Ignoring: '%s'", url)
                continue
            name = url.split('/')[4]
            if car.picture.img.get('alt'):
                name = car.picture.img.get('alt')
            data[name] = {'url': settings.AUTOMOBILE_TN_BASE_URL + url,
                           'img_url': car.picture.img.get('src'),
                        }

    return data


def get_cars_infos(url):
    response = requests.get(url, proxies=proxyDict, headers=headersDict)
    data = {}
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        versions = soup.find_all(class_='versions-details')
        version_models = {}
        if versions:
            for _element in versions[0].tbody.find_all('tr'):
                version_models[_element.a.text.strip()] = settings.AUTOMOBILE_TN_BASE_URL + _element.a.get('href')
        else:
            version_models[soup.find(class_='version-img').picture.img.get('alt')] = url

        for car_version, version_url in version_models.items():
            car_version_resp = requests.get(version_url, proxies=proxyDict, headers=headersDict)
            soup_version = BeautifulSoup(car_version_resp.text, 'html.parser')
            car_title = soup_version.find(class_="bloc-title").h3.text
            car_title_span = soup_version.find(class_="bloc-title").h3.span.text
            car_title_span_spaced = " %s" % car_title_span
            if car_title_span_spaced not in car_title:
                car_title = car_title.replace(car_title_span, car_title_span_spaced)
            version = soup_version.find_all(class_="version-details")[0]
            img_url = version.find_all(class_='version-img')[0].picture.img.get('src')
            specs = version.find_all(class_='technical-details')[0]
            spec_detail = {'img_url': img_url}
            for field, dest_field in CAR_FIELD.items():
                if specs.find("th", text=field):
                    value = specs.find("th", text=field).find_next_sibling("td")
                    if field == "Transmission":
                        value = specs.find_all("th", text=field)[1].find_next_sibling("td")
                    if value:
                        value = value.text
                    else:
                        value = ""
                    spec_detail[dest_field] = value.strip()
                else:
                    logger.info('Could not retrieve "%s" from source for Car model "%s".',
                                field, car_title)
                    spec_detail[dest_field] = ''

            data[car_title] = spec_detail

    return data
# brands = get_brand_dict()
#
# for brand, details in brands.items():
#     img_url = details['img_url'].split('?')[0]
#     img_name = img_url.split('/')[-1]
#     img_hash, img_ext = get_name_extension(img_name)
#     # save brand into DB
#     download_images(img_url, img_hash+".png")
#     print(brand)
#
# pprint.pprint(brands)

# url = "https://www.automobile.tn/fr/neuf/audi/q3"
# resp = get_cars_infos(url)
# pprint.pprint(resp)
# {'35 TFSI S-tronic Advanced': {'air_conditioner': 'Automatique | Bizone',
#                                'category': 'SUV',
#                                'cylindre': '1498 CM³',
#                                'door_nbr': '5',
#                                'energy': 'Essence',
#                                'extra_urban_consumption': '5.1 L/100 km',
#                                'gear': 'Automatique',
#                                'gear_nbr': '6',
#                                'height': '1616 mm',
#                                'horse_power': '8 CV',
#                                'img_url': 'https://catalogue.automobile.tn/big/2019/09/46244.jpg?t=1642084213',
#                                'length': '4484 mm',
#                                'mixte_consumption': '5.7 L/100 km',
#                                'place_nbr': '5',
#                                'trunk_volume': '530 L',
#                                'urban_consumption': '6.9 L/100 km',
#                                'vitesse_max': '207 KM/H',
#                                'width': '1856 mm'},
#  '35 TFSI S-tronic Advanced Plus': {'air_conditioner': 'Automatique | Bizone',
#                                     'category': 'SUV',
#                                     'cylindre': '1498 CM³',
#                                     'door_nbr': '5',
#                                     'energy': 'Essence',
#                                     'extra_urban_consumption': '5.1 L/100 km',
#                                     'gear': 'Automatique',
#                                     'gear_nbr': '6',
#                                     'height': '1616 mm',
#                                     'horse_power': '8 CV',
#                                     'img_url': 'https://catalogue.automobile.tn/big/2021/01/46488.jpg?t=1642084228',
#                                     'length': '4484 mm',
#                                     'mixte_consumption': '5.7 L/100 km',
#                                     'place_nbr': '5',
#                                     'trunk_volume': '530 L',
#                                     'urban_consumption': '6.9 L/100 km',
#                                     'vitesse_max': '207 KM/H',
#                                     'width': '1856 mm'}}

# url = "https://www.automobile.tn/fr/neuf/audi/q8/55-tfsi-tiptronic-quattro"
# resp = get_cars_infos(url)
# import json
# print(json.dumps(resp, ensure_ascii=False, indent=4))
