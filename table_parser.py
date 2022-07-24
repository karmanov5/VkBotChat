import json, re, requests
from bs4 import BeautifulSoup
from fuzzywuzzy import process

url = 'https://fitaudit.ru/food'

def get_data_from_json_file():
    with open('table_data/data.json', encoding='utf-8') as file:
        data = json.load(file)
        data_dict = dict()
        pattern = re.compile(r'([\d|,]+)')
        i, j = 1, 1
        print("Начало процесса парсинга страниц сайта")
        for category, products in data.items():
            data_dict[category] = []
            print(f"{i} - {len(data) - i} Категория продукта: {category}")
            for product in products:
                product_dict = dict()
                name, href = product.values()
                product_dict['Название продукта'] = name
                res = requests.get(href).content.decode('utf-8')
                bs = BeautifulSoup(res, 'lxml')
                table = bs.find_all('span', class_='pr__fl')
                fat, proteins, carbohydrate = [pattern.search(row.find(class_='js__msr_cc').text).group(1).replace(',', '.')
                                               for row in table[:3]]
                calories = pattern.search(bs.find('span', class_='him_bx__legend_text').find('span').text).group(1)
                product_dict['Белки'] = proteins
                product_dict['Жиры'] = fat
                product_dict['Углеводы'] = carbohydrate
                product_dict['Энергия'] = calories
                print(f'{i}: {j} - {len(products) - j} {name} - OK')
                data_dict[category].append(product_dict)
                j += 1
            j = 1

            i += 1
        with open('table_data/data_output.json', 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=4)

def get_data():
    with open('table_data/data_output.json', encoding='utf-8') as f:
        data = json.load(f)
        req = open('reqs.txt', encoding='utf-8').read().strip()
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
                for category, products in data.items():
                    for product in products:
                        n, p = process.extractOne(name, [product['Название продукта']])
                        if p >= 75:
                            p_max = max(p_max, p)
                            result_dict.append(({'категория':category,
                                                'название продукта':product['Название продукта'],
                                                'белки':product['Белки'],
                                                'жиры':product['Жиры'],
                                                'углеводы':product['Углеводы'],
                                                'калории':product['Энергия'],
                                                }, p))
                result_dict = list(filter(lambda d: d[-1] == p_max, result_dict))
                if len(result_dict) > 1:
                    print(f'Неточный запрос! Ваш запрос: {name}. Возможно вы имели в виду:')
                    # print(result_dict)
                    print(', '.join(name[0]['название продукта'] for name in result_dict))
                    is_correct_flag = False
                else:
                    product = result_dict[0][0]
                    # print(float(product['белки']) / 100 * count)
                    proteins += int(round(float(product['белки']) / 100 * count))
                    fats += int(round(float(product['жиры']) / 100 * count))
                    carbohydrate += int(round(float(product['углеводы']) / 100 * count))
                    calories += int(round(float(product['калории']) / 100 * count))
        if is_correct_flag: print(f'Итого: {proteins} б, {fats} ж, {carbohydrate} у, {calories} ккал')


        # for match in re.findall(r'(?P<name>\w{2,}?\s*?\w+)\s*?(?P<count>\d+)', req):
        #     name, count = match
        #     result_dict = list()
        #     p_max = 0
        #     for category, products in data.items():
        #         for product in products:
        #             n, p = process.extractOne(name, [product['Название продукта']])
        #             if p >= 75:
        #                 p_max = max(p_max, p)
        #                 result_dict.append((category, product['Название продукта'], p))
        #     result_dict = list(filter(lambda d: d[-1] == p_max, result_dict))
        #     if len(result_dict) > 1:
        #         print('Возможно вы имели в виду:')
        #         print(', '.join(name[1] for name in result_dict))
        #     else:
        #         proteins, fats, carbohydrates = 0, 0, 0
        #         print(result_dict)


def main():
    get_data()

if __name__ == '__main__':
    main()