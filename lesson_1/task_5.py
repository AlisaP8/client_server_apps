"""
5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.
"""

import subprocess


def sub_ping(service):
    args = ['ping', service]
    ping = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in ping.stdout:
        line = line.decode('cp866').encode('utf-8')
        print(line.decode('utf-8'))


sub_ping('yandex.ru')
sub_ping('youtube.com')
