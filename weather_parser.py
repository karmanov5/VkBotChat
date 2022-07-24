from bs4 import BeautifulSoup
import urllib.request as req
import re, datetime, threading
from time import sleep
from city_get_id import get_city_id


class weather_parser():


    def __init__(self, save_logs):
        self.save_logs = save_logs
        pass
        # self._time = datetime.datetime.now()
        
        # self._start_routine()

    def _get_data(self, city='Югыдъяг'):
        try:
            city_name, id = get_city_id(city)
            url = f'https://yandex.ru/pogoda/?{id}'
            data = req.urlopen(url).read()
            with open(f'data/index-{city_name}.html', 'wb') as f:
                f.write(data)
            return city_name, data, url
        except Exception as ex:
            self.save_logs(str(ex))
            print('Сетевая ошибка!')
            print(ex)

    
    def get_current_forecast(self, city=None):
        if not city: city = 'Югыдъяг'
        city_name, data, url = self._get_data(city)
        result = ''
        if data:
            bs = BeautifulSoup(data.decode('utf-8'), 'lxml')
            """Текущая погода"""
            result = f'Погода, {city_name}\nТемпература воздуха: '
            result += bs.find(class_='temp fact__temp fact__temp_size_s').text + "°\n"
            result += bs.find(class_='link__feelings fact__feelings').find(class_='link__condition day-anchor i-bem').text + ', '
            result += 'ощущается как ' + bs.find(class_='term term_orient_h fact__feels-like').find(class_='temp__value temp__value_with-unit').text + '°\n'
            result += 'Скорость ветра: ' + bs.find(class_='fact__props').find(class_='term__value').text + '\n'
            result += bs.find(class_='maps-widget-fact__title').text + '\n'
            result += f'Подробнее: {url}'
        else:
            result += 'Произошла внутренняя ошибка!'
        return result

    def get_current_forecast_morning(self):
        city_name, data, url = self._get_data('Югыдъяг')
        if data:
            bs = BeautifulSoup(data.decode('utf-8'), 'lxml')
            result = 'Погода на сегодня, Югыдъяг: \n'
            result += 'Температура воздуха: '
            result += bs.find(class_='temp fact__temp fact__temp_size_s').text + "°\n"
            result += bs.find(class_='link__feelings fact__feelings').find(class_='link__condition day-anchor i-bem').text + ', '
            result += 'ощущается как ' + bs.find(class_='term term_orient_h fact__feels-like').find(class_='temp__value temp__value_with-unit').text + '°\n'
            result += 'Скорость ветра: ' + bs.find(class_='fact__props').find(class_='term__value').text + '\n'
            result += bs.find(class_='maps-widget-fact__title').text + '\n'
            result += 'Почасовой прогноз:\n'
            hourly_weather = bs.find(class_='swiper-container fact__hourly-swiper').find_all(class_='fact__hour swiper-slide')
            hour_weather = [
                re.sub(r'\d+ час[\w]*', hour_w.find(class_='fact__hour-label').text, hour_w.find(class_='a11y-hidden').text)
                for hour_w in hourly_weather
            ]
            is_tomorrow_flag = False
            for hour in hour_weather:
                is_tomorrow_flag += (re.search(r'\b0\:00', hour) is not None)
                result += hour + '\n'
                if is_tomorrow_flag: break
            result += 'Отличного вам дня!'
            return result
        else:
            return 'Произошла ошибка на сервере!'

    def get_current_forecast_evening(self):
        city_name, data, url = self._get_data('Югыдъяг')
        if data:
            bs = BeautifulSoup(data.decode('utf-8'), 'lxml')
            result = 'Погода на завтра, Югыдъяг: \n'
            hourly_weather = bs.find(class_='swiper-container fact__hourly-swiper').find_all(class_='fact__hour swiper-slide')
            hour_weather = [
                re.sub(r'\d+ час[\w]*', hour_w.find(class_='fact__hour-label').text, hour_w.find(class_='a11y-hidden').text)
                for hour_w in hourly_weather
            ]
            forecast_briefly = bs.find(class_='forecast-briefly__days swiper-container').find_all('li')
            day_labels = ['day', 'daytime', 'condition', 'day_temp', 'nigth_temp']
            days_forecast = [
                dict(zip(day_labels, re.split(r', ', day.find('a').get('aria-label')))) 
                # day.find('a').get('aria-label')
                for day in forecast_briefly
            ]
            result += ', '.join((days_forecast[2]['condition'], days_forecast[2]['day_temp'], days_forecast[2]['nigth_temp'])) + '\n'
            result += 'Почасовой прогноз: \n'
            
            is_tomorrow_flag = False
            for hour in hour_weather:
                is_tomorrow_flag += (re.search(r'\b0\:00', hour) is not None)
                if is_tomorrow_flag: result += hour + '\n'
            result += 'Спокойной ночи!'
            return result
        else:
            return 'Произошла ошибка на сервере!'

    def get_hourly_weather(self, city=None, key=None, add_time=False, is_tomorrow=False):
        if not city: city = 'Югыдъяг'
        city_name, data, url = self._get_data(city)
        result = ''
        if data:
            bs = BeautifulSoup(data.decode('utf-8'), 'lxml')
            hourly_weather = bs.find(class_='swiper-container fact__hourly-swiper').find_all(class_='fact__hour swiper-slide')
            hour_weather = [
                re.sub(r'\d+ час[\w]*', hour_w.find(class_='fact__hour-label').text, hour_w.find(class_='a11y-hidden').text)
                for hour_w in hourly_weather
            ]
            if key:
                if is_tomorrow:
                    result = f'{city_name}, завтра:\n'
                else:
                    result = f'{city_name}, сегодня:\n'
                
                if add_time:
                    number = 1
                    if re.search(r'(\d\d?)', key):
                        number = int(re.search(r'(\d\d?)', key).group(1))
                    time = datetime.datetime.now() + datetime.timedelta(hours=number)
                    delta = datetime.timedelta(hours=time.hour, minutes=time.minute)
                    deltasec = round(delta.seconds / 3600) * 3600
                    for h in hour_weather:
                        if str(datetime.timedelta(seconds=deltasec))[:-3] in h:
                            result += h + '\n'
                            break
                else:
                    if re.search(r'(\d\d?\:\d\d)', key):
                        if is_tomorrow:
                            tomorrow_flag = False
                            for h in hour_weather:
                                tomorrow_flag += (re.search(r'\b0\:00', h) is not None)
                                if (re.search(r'(\d\d?\:\d\d)', key).group(1) in h) and tomorrow_flag:
                                    result += h + '\n'
                                    break
                        else:
                            for h in hour_weather:
                                if re.search(r'(\d\d?\:\d\d)', key).group(1) in h:
                                    result += h + '\n'
                                    break
                    else:
                        number = '1'
                        if re.search(r'(\d\d?)', key):
                            number = re.search(r'(\d\d?)', key).group(1)
                        if len(number) > 1 and number[0] == '0':
                            number = number[1]
                        number = number + ":00"
                        if is_tomorrow:
                            tomorrow_flag = False
                            for h in hour_weather:
                                tomorrow_flag += (re.search(r'\b0\:00', h) is not None)
                                if (number in h) and tomorrow_flag:
                                    result += h + '\n'
                                    break
                        else:
                            for h in hour_weather:
                                if number in h:
                                    result += h + '\n'
                                    break
            else:
                """Почасовая погода"""
                if is_tomorrow:
                    result = f'Почасовая погода на завтра, {city_name}: \n'
                else: result = f'Почасовая погода в {city_name}: \n'
                is_tomorrow_flag = False
                for hour in hour_weather:
                    is_tomorrow_flag += (re.search(r'\b0\:00', hour) is not None)
                    if is_tomorrow:
                        if is_tomorrow_flag: result += hour + '\n'
                    else:
                        result += hour + '\n'
                        if is_tomorrow_flag: break
            result += f'Подробнее: {url}'             
        else: result += 'Произошла внутренняя ошибка!'
        return result

    def get_weekly_weather(self, city=None, is_next_week=False):
        if not city: city = 'Югыдъяг'
        city_name, data, url = self._get_data(city)
        result = ''
        bs = BeautifulSoup(data.decode('utf-8'), 'lxml')
        forecast_briefly = bs.find(class_='forecast-briefly__days swiper-container').find_all('li')
        day_labels = ['day', 'daytime', 'condition', 'day_temp', 'nigth_temp']
        days_forecast = [
            dict(zip(day_labels, re.split(r', ', day.find('a').get('aria-label')))) 
            # day.find('a').get('aria-label')
            for day in forecast_briefly
        ]
        if is_next_week:
            result = f'Погода на следующую неделю, {city_name}:\n'
            is_monday, count = False, 0
            for day in days_forecast:
                is_monday += day['day'] == 'понедельник'
                if is_monday:
                    result += ', '.join(day.values()) + '\n'
                    count += 1
                if count > 6: break
        else:
            result += f'Погода на этой неделе, {city_name}\n'
            is_monday = False
            for day in days_forecast:
                is_monday += day['day'] == 'понедельник'
                if is_monday:
                    break
                result += ', '.join(day.values()) + '\n'
        result += f'Подробнее: {url}'
        return result

    def get_start_to_end_hour_forecast(self, start_hour:str, end_hour:str, is_tomorrow=False, city=None):
        if not city: city = 'Югыдъяг'
        city_name, data, url = self._get_data(city)
        result = ''
        if data:
            if is_tomorrow: result = f'Погода завтра с {start_hour} по {end_hour}, {city_name}:\n' 
            else: result = f'Погода с {start_hour} по {end_hour}, {city_name}:\n'    
            bs = BeautifulSoup(data.decode('utf-8'), 'lxml')
            hourly_weather = bs.find(class_='swiper-container fact__hourly-swiper').find_all(class_='fact__hour swiper-slide')
            hour_weather = [
                re.sub(r'\d+ час[\w]*', hour_w.find(class_='fact__hour-label').text, hour_w.find(class_='a11y-hidden').text)
                for hour_w in hourly_weather
            ]
            if re.search(r'(\d\d?\:\d\d)', start_hour) is None: start_hour = re.search(r'(\d?\d)', start_hour).group(1) + ':00'
            if re.search(r'(\d\d?\:\d\d)', end_hour) is None: end_hour = re.search(r'(\d?\d)', end_hour).group(1) + ':00'
            
            if is_tomorrow:
                is_tomorrow_hour = False
                is_start_hour = False
                for hour in hour_weather:
                    is_tomorrow_hour += (re.search(r'\b0\:00', hour) is not None)
                    if is_tomorrow_hour:
                        is_start_hour += start_hour in hour
                        if is_start_hour:
                            result += hour + '\n'
                        if end_hour in hour:
                            break
            else:
                is_start_hour = False
                for hour in hour_weather:
                    is_start_hour += start_hour in hour
                    if is_start_hour:
                        result += hour + '\n'
                    if end_hour in hour:
                        break
            if not is_start_hour: return 'Неправильно указано начальное время! Начальное время должно быть больше либо равным текущему!'
            result += f'Подробнее: {url}'
            return result

    
    def get_start_to_end_day_forecast(self, start_date:str, end_date:str, city=None):
        if not city: city = 'Югыдъяг'
        city_name, data, url = self._get_data(city)
        result = ''
        if data:
            result = f'Погода с {start_date} по {end_date}, {city_name}:\n'
            bs = BeautifulSoup(data.decode('utf-8'), 'lxml')
            forecast_briefly = bs.find(class_='forecast-briefly__days swiper-container').find_all('li')
            day_labels = ['day', 'daytime', 'condition', 'day_temp', 'nigth_temp']
            days_forecast = [
                dict(zip(day_labels, re.split(r', ', day.find('a').get('aria-label')))) 
                # day.find('a').get('aria-label')
                for day in forecast_briefly
            ]
            is_start_date = False
            for day in days_forecast:
                is_start_date += day['daytime'] == start_date
                if is_start_date:
                    result += ', '.join(day.values()) + '\n'
                if day['daytime'] == end_date:
                    break
            if not is_start_date: return 'Неправильно указана начальная дата! Начальная дата должна быть больше текущей, либо равной ей!'
            result += f'Подробнее: {url}'
            return result

    def get_dayly_forecast(self, city=None, date_key=None):
        if not city: city = 'Югыдъяг'
        city_name, data, url = self._get_data(city)
        result = ''
        if data:
            bs = BeautifulSoup(data.decode('utf-8'), 'lxml')
            forecast_briefly = bs.find(class_='forecast-briefly__days swiper-container').find_all('li')
            day_labels = ['day', 'daytime', 'condition', 'day_temp', 'nigth_temp']
            days_forecast = [
                dict(zip(day_labels, re.split(r', ', day.find('a').get('aria-label')))) 
                # day.find('a').get('aria-label')
                for day in forecast_briefly
            ]
            if date_key:
                result = f'Погода на {date_key}, {city_name}: \n'
                if date_key == 'завтра':
                    result += ', '.join((days_forecast[2]['condition'], days_forecast[2]['day_temp'], days_forecast[2]['nigth_temp'])) + '\n'
                else:
                    result += ''.join(map(lambda d: ', '.join((d['condition'], d['day_temp'], d['nigth_temp'])), 
                    [day for day in days_forecast if day['day'] == date_key or day['daytime'] == date_key]))  + '\n'
            else:
                """Погода по дням"""
                result = f'Погода по дням, {city_name}: \n'
                result += '\n'.join(map(lambda d: d.values(), days_forecast))
        else: result = 'Произошла внутренняя ошибка!'
        result += f'Подробнее: {url}'
        return result


    # def _start_routine(self):
    #     def start(self):
    #         while True:
    #             sleep(600)
    #             self.data = self._get_data()
    #             self.bs = BeautifulSoup(self.data.decode('utf-8'), 'lxml')
    #     threading.Thread(target=start, args=(self,)).start()





