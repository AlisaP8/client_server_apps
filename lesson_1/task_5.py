"""
5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.
"""
import platform
import subprocess
import chardet


urls = ['yandex.ru', 'youtube.com']
param = '-n' if platform.system().lower() == 'windows' else '-c'

for url in urls:
    args = ['ping', param, '2', url]
    sub_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
    # print(type(sub_ping))
    for line in sub_ping.stdout:
        result = chardet.detect(line)
        print('sub_ping = ', result)
        line = line.decode(result['encoding']).encode('utf-8')
        print(line.decode('utf-8'))



