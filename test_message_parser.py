import re

samples = open('sample.txt', encoding='utf-8').readlines()
for sample in samples:
    if re.search(r'[Бб]от.*?погода.*?([А-Я]\w*)', sample):
        print(re.search(r'[Бб]от.*?погода.*?([А-Я]\w*)', sample).group(1))


# bot_name = re.search(r'[Бб]от')