import json
import requests
import re


def get_city_id(city_name):
    url = f'https://suggest-maps.yandex.ru/suggest-geo?callback=jQuery&v=8&lang=ru_RU&search_type=weather&part={city_name[:-1]}'
    res = requests.get(url=url)
    res = res.text.replace('jQuery(', '').replace('])', ']')
    j = json.loads(res)
    dictionary = j[1][0]
    return dictionary['name_short'], 'lat={lat}&lon={lon}'.format(lat=dictionary['lat'], lon=dictionary['lon'])
