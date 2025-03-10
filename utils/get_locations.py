import requests
import time
import re
import json
import pprint
from bs4 import BeautifulSoup

from selenium import webdriver

driver = webdriver.Firefox()
driver.get('https://www.google.com/maps/')

HTTP_PROXY = ""
#HTTP_PROXY = "http://10.66.243.130:8080"

proxyDict = {
              "http"  : HTTP_PROXY,
              "https" : HTTP_PROXY,
              "ftp"   : HTTP_PROXY
            }

countries = [
    'Kasserine',
    'Kebili',
    'Le Kef',
    'Mahdia',
    'Mannouba',
    'Medenine',
    'Monastir',
    'Nabeul',
    'Sfax',
    'Sidi Bouzid',
    'Siliana',
    'Sousse',
    'Tataouine',
    'Tozeur',
    'Tunis',
    'Zaghouan',
    'Ariana',
    'Beja',
    'Ben Arous',
    'Bizerte',
    'Gabes',
    'Gafsa',
    'Jendouba',
    'Kairouan',
    ]

#countries = ['Tozeur']

def get_location(delegation, name, driver):
    if not driver:
        driver = webdriver.Firefox()
    url = "https://www.google.com/maps/place?q=%s,%s" % (name, delegation)
    driver.get(url)



    i = 0
    _match = re.search(r'.*\@([^,]*),([^,]*),(.*z)/.*', driver.current_url)
    while not _match:
        #print(i)
        time.sleep(1)
        _match = re.search(r'.*\@([^,]*),([^,]*),(.*z)/.*', driver.current_url)
        i = i + 1
        if i > 15:
            break

    if _match:
        return _match.group(1), _match.group(2)
    print(driver.current_url)

    return '', ''

# res = get_location('Zaghouan', 'Ain Lansarine', driver)
#
# print(res)

data = {}
for country in countries:
    start = time.time()
    lc = country.lower().replace(' ', '-')
    data[country] = {}

    url = "https://www.azpostcodes.com/tun/state-%s/" % lc
    response = requests.get(url, proxies=proxyDict)
    print(country)
    # get delegations
    soup = BeautifulSoup(response.text, 'html.parser')
    for el in soup.find_all('td'):
        deleg = {}
        #print("--> ", el)
        if not el.a:
            delegation = el.get_text().strip()
            data[country][delegation] = {}
            data[country][delegation]['delegation'] = [{"locality": []}]
            data[country][delegation]['lat'], data[country][delegation]['lon'] = get_location(country, delegation, driver)

            deleg = {}
            continue
        delegation = el.a.get_text().strip()
        data[country][delegation] = {}
        data[country][delegation]['delegation'] = []
        #print(delegation)
        delegation_link = "https://www.azpostcodes.com" + el.a.get('href')
        deleg = {'locality': []}
        del_resp = requests.get(delegation_link, proxies=proxyDict)
        del_soup = BeautifulSoup(del_resp.text, 'html.parser')
        table = del_soup.find_all(class_='table-responsive')[0]
        # table = del_soup.find_all("div", {"class": "card mb-2"})[0]

        for del_el in table.find_all('tr'):
            ddd = del_el.find_all('td')
            #print(ddd)
            if len(ddd) == 0:
                continue
            if len(ddd) == 4 and ddd[3].a.get('href'):
                href = ddd[3].a.get('href')
                _match = re.search( r'.*lat=(.*)\&long=(.*)\&.*', href)
            else:
                _match = None
            # page 1 , 2 , 3 ..
            if not ddd[0].a:
                print('>>>> ', ddd[0])
                continue

            #print(ddd[0].a.get_text().strip())
            zipcode = ''
            if len(ddd) > 1:
                zipcode = ddd[1].get_text()
            locality = {'name': ddd[0].a.get_text().strip(),
                                         'zipcode': zipcode.split(',')[0].strip(),
                                         'lat': '',
                                         'lon': ''
                                         }
            if _match:
                locality['lat'] = _match.group(1)
                locality['lon'] = _match.group(2)

            if not locality['lat'] or locality['lat'] == 'None':
                locality['lat'], locality['lon'] = get_location(delegation, locality['name'], driver)

            deleg['locality'].append(locality)

            #break
        data[country][delegation]['delegation'].append(deleg)
        data[country][delegation]['lat'], data[country][delegation]['lon'] = get_location(country, delegation, driver)
        #break

    data[country]['lat'], data[country]['lon'] = get_location(country, country, driver)
    print("%s computed in %s seconds" % (country, time.time() - start))

    with open("city_json/%s.json" % country.replace(' ', '_'), "w") as outfile:
        json.dump({country: data[country]}, outfile, indent=4)

    #break

driver.close()
#pprint.pprint(data)

with open("city_json/tunisia_cities.json", "w") as outfile:
    json.dump(data, outfile, indent=4)

