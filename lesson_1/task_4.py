"""
4. Преобразовать слова «разработка», «администрирование», «protocol», «standard»
из строкового представления в байтовое и выполнить обратное преобразование
(используя методы encode и decode).
"""

VAR_1 = 'разработка'
VAR_2 = 'администрирование'
VAR_3 = 'protocol'
VAR_4 = 'standard'

STR = [VAR_1, VAR_2, VAR_3, VAR_4]

for items in STR:
    item_1 = items.encode('utf-8')
    item_2 = items.encode('utf-8').decode('utf-8')
    print(f'{item_1} - {item_2}')

