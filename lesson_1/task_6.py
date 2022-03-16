"""
6. Создать текстовый файл test_file.txt, заполнить его тремя строками:
«сетевое программирование», «сокет», «декоратор».
Далее забыть о том, что мы сами только что создали этот файл и
исходить из того, что перед нами файл в неизвестной кодировке.
Задача: открыть этот файл БЕЗ ОШИБОК вне зависимости от того, в какой кодировке он был создан.
"""
from chardet import detect


# создаем файл
test = open('test_file.txt', 'w', encoding='utf-8')
test.write('сетевое программирование \nсокет \nдекоратор')
test.close()


# узнаем кодировку
with open('test_file.txt', 'rb') as test:
    content = test.read()
encode = detect(content)['encoding']
# print('encoding: ', encode)


# открываем файл
with open('test_file.txt', 'r', encoding=encode) as f_test:
    content = f_test.read()
print(content)


# with open('test_file.txt', encoding=encoding) as f_test:
#     for el in f_test:
#         print(el, end='')
#     print()
