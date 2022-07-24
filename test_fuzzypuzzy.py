from fuzzywuzzy import process

with open('table_data/names.txt', encoding='utf-8') as f:
    s1 = f.readlines()
s2 = 'Рис'

# print([b[0] for b in process.extractBests(s2, s1) if b[1] >= 80])
print(process.extract(s2, s1))