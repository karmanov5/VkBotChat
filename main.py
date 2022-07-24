from datetime import datetime
import threading
from time import sleep
import vk_api, re, random
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import api_key
from weather_parser import weather_parser
from calories import calorizator

vk_session = vk_api.VkApi(token=api_key)
vk = vk_session.get_api()


def send_message(chat_id, message):
    vk.messages.send(
        chat_id=chat_id,
        message=message,
        random_id=random.randint(1, 1000)
    )


def main():
    weather = weather_parser(save_logs=save_logs)
    calories = calorizator(save_logs=save_logs)
    start_task(weather=weather)
    save_logs('Запущен бот')
    while True:
        longpool = VkBotLongPoll(vk_session, 214497515)
        try:
            for event in longpool.listen():
                if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat:
                    message_text = event.message['text']
                    chat_id = event.chat_id
                    save_logs(message_text)
                    print(message_text)

                    if 'бот' in message_text.lower():
                        if 'погод' in message_text.lower():
                            city_name = None
                            # Проверка на наличие города в запросе
                            if re.search(r'[Бб]от.*?погода.*?([А-Я]\w*)', message_text):
                                city_name = re.search(r'[Бб]от.*?погода.*?(?P<city>[А-Я]\w*)', message_text).group(
                                    'city')
                            if re.search(r'(часов[ой|ая]|по.*?часам|подробный)', message_text):
                                send_message(chat_id, message=weather.get_hourly_weather(city_name,
                                                                                         is_tomorrow='завтра' in message_text.lower()))
                            # проверка на наличие ключевых слов с часу на час
                            elif re.search(
                                    r'(?P<start>\d?\d?\s*?час.*?\b|\d\d?\:\d\d).*?[по|-|до].*?(?P<end>\d?\d?\s*?час.*?\b|\d\d?\:\d\d)',
                                    message_text):
                                start_hour = re.search(
                                    r'(?P<start>\d?\d?\s*?час.*?\b|\d\d?\:\d\d).*?[по|-|до].*?(?P<end>\d?\d?\s*?час.*?\b|\d\d?\:\d\d)',
                                    message_text).group('start')
                                end_hour = re.search(
                                    r'(?P<start>\d?\d?\s*?час.*?\b|\d\d?\:\d\d).*?[по|-|до].*?(?P<end>\d?\d?\s*?час.*?\b|\d\d?\:\d\d)',
                                    message_text).group('end')
                                send_message(chat_id,
                                             message=weather.get_start_to_end_hour_forecast(start_hour, end_hour,
                                                                                            'завтра' in message_text.lower(),
                                                                                            city_name))
                            # Проверка на наличие ключевых слов Завтра на определенное время
                            elif re.search(r'([Зз]автра.*?\d\d?.*?\w+\b)', message_text):
                                send_message(chat_id, message=weather.get_hourly_weather(city_name, re.search(
                                    r'(\d?\d?\s*?час.*?\b|\d\d?\:\d\d)', message_text).group(1),
                                                                                         'через' in message_text, True))
                            # проверка на наличие ключевых слов через час, на определенное время
                            elif re.search(r'(\d?\d?\s*?час.*?\b|\d\d?\:\d\d)', message_text):
                                send_message(chat_id, message=weather.get_hourly_weather(city_name, re.search(
                                    r'(\d?\d?\s*?час.*?\b|\d\d?\:\d\d)', message_text).group(1),
                                                                                         'через' in message_text))
                            # проверка на наличие ключевых слов с определенного числа месяца по определенное число месяца
                            elif re.search(r'(?P<start>\d\d?.*?\w+\b).*?[по|-].*?(?P<end>\d\d?.*?\w+\b)', message_text):
                                start_date = re.search(r'(?P<start>\d\d?.*?\w+\b).*?[по|-].*?(?P<end>\d\d?.*?\w+\b)',
                                                       message_text).group('start')
                                end_date = re.search(r'(?P<start>\d\d?.*?\w+\b).*?[по|-].*?(?P<end>\d\d?.*?\w+\b)',
                                                     message_text).group('end')
                                send_message(chat_id,
                                             message=weather.get_start_to_end_day_forecast(start_date=start_date,
                                                                                           end_date=end_date,
                                                                                           city=city_name))

                            # проверка на наличие ключевых слов сегодня, завтра или другую дату
                            elif re.search(r'([Зз]автра|[Сс]егодня|\d\d?.*?\w+\b)', message_text):
                                send_message(chat_id, message=weather.get_dayly_forecast(city_name, re.search(
                                    r'([Зз]автра|[Сс]егодня|\d\d?.*?\w+\b)', message_text).group(1)))

                            # проверка на наличие ключевых слов неделя, следующая неделя
                            elif re.search(r'(?P<week>недел\w+)', message_text):
                                send_message(chat_id,
                                             message=weather.get_weekly_weather(city_name, 'следую' in message_text))

                            else:
                                send_message(chat_id, message=weather.get_current_forecast(city_name))
                        # Ответ на спасибо
                        elif any(word in message_text.lower() for word in ("спасибо", "спс", "благодарю", "thanks")):
                            send_message(chat_id, message='Да не за что!')

                        # Отправка результата работы подсчета калорий если в запросе есть слово калории
                        elif 'калор' in message_text.lower():
                            send_message(chat_id, message=calories.get_calories_from_food(message_text.lower()))

                        else:
                            pass
                    elif 'инфо' in message_text.lower():
                        send_message(chat_id=chat_id, message="""
                        Привет, меня зовут Бот. 
                        Я выдаю краткую информацию пока что о погоде. 
                        В скором времени я научусь делать и другие вещи.
                        А пока что я выдаю краткую информацию о погоде в каком-нибудь месте.
                        Информацию о погоде я беру с сервиса Яндекс.Погода. 
                        У меня есть одна особенность, если спросить погоду на другой день, кроме завтра в определенное время, 
                        то я такую информацию пока что представить не могу.
                        Чтобы узнать о погоде, нужно обратиться ко мне 
                        "бот, скажи погоду на завтра в таком-то городе (обязательно с большой буквы!)" 
                        или 
                        "бот, погода", 
                        и я попробую предоставить тебе нужную информацию
                        """)






        except Exception as ex:
            save_logs(str(ex))
            continue


def save_logs(string: str):
    with open('logs.txt', 'a', encoding='utf-8') as f:
        message = datetime.now().strftime('%H:%M:%S') + f': {string}\n'
        f.write(message)


def start_task(weather: weather_parser):
    def task(_weather: weather_parser):
        while True:
            now = datetime.now()
            if now.strftime('%H:%M:%S') == '07:00:00':
                send_message(chat_id=4, message=_weather.get_current_forecast_morning())
            elif now.strftime('%H:%M:%S') == '22:00:00':
                send_message(chat_id=4, message=_weather.get_current_forecast_evening())
            sleep(1)

    threading.Thread(target=task, args=(weather,)).start()


if __name__ == '__main__':
    main()
