import json, re
from fuzzywuzzy import process


class calorizator:

    def __init__(self, save_logs):
        self.save_logs = save_logs
        with open('table_data/data_output.json', encoding='utf-8') as f:
            self._data = json.load(f)


    def get_calories_from_food(self, request: str):
        try:
            incorrect_result = ''
            req = request.strip()
            reqs = req.split('\n')
            pattern = re.compile(r'(?P<name>[\w|\s]*?)\s*(?P<count>\d+)\s*(?P<units>\w+)')
            proteins, fats, carbohydrate, calories = 0, 0, 0, 0
            is_correct_flag = True
            for req in reqs[1:]:
                s = pattern.search(req)
                if s:
                    name, count, units = s.group('name'), int(s.group('count')), s.group('units')
                    result_dict = list()
                    p_max = 0
                    for category, products in self._data.items():
                        for product in products:
                            n, p = process.extractOne(name, [product['Название продукта']])
                            if p >= 75:
                                p_max = max(p_max, p)
                                result_dict.append(({'категория': category,
                                                     'название продукта': product['Название продукта'],
                                                     'белки': product['Белки'],
                                                     'жиры': product['Жиры'],
                                                     'углеводы': product['Углеводы'],
                                                     'калории': product['Энергия'],
                                                     }, p))
                    result_dict = list(filter(lambda d: d[-1] == p_max, result_dict))
                    if len(result_dict) > 1:
                        incorrect_result += f'Неточный запрос! Ваш запрос: {name}. Возможно вы имели в виду:'
                        # print()
                        # # print(result_dict)
                        incorrect_result += '\n- ' + '\n- '.join(name[0]['название продукта'] for name in result_dict) + '\n'
                        is_correct_flag = False
                    else:
                        product = result_dict[0][0]
                        # print(float(product['белки']) / 100 * count)
                        proteins += int(round(float(product['белки']) / 100 * count))
                        fats += int(round(float(product['жиры']) / 100 * count))
                        carbohydrate += int(round(float(product['углеводы']) / 100 * count))
                        calories += int(round(float(product['калории']) / 100 * count))
            if is_correct_flag: return f'Итого: {proteins} б, {fats} ж, {carbohydrate} у, {calories} ккал'
            else: return incorrect_result
        except Exception as ex:
            self.save_logs(ex)
            return 'Произошла ошибка при парсинге БД!'

        

        