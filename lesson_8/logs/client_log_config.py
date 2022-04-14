import logging
import os
import sys

sys.path.append('../')

client_formatter = logging.Formatter('%(asctime)-25s %(levelname)-10s %(filename)-22s %(message)s')

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client.log')

stream_hand = logging.StreamHandler()
stream_hand.setFormatter(client_formatter)
stream_hand.setLevel(logging.ERROR)
log_file = logging.FileHandler(PATH, encoding='utf-8')
log_file.setFormatter(client_formatter)

log = logging.getLogger('client')
log.addHandler(stream_hand)
log.addHandler(log_file)
log.setLevel(logging.DEBUG)

if __name__ == '__main__':
    log.debug('Отладочная информация')
    log.info('Информационное сообщение')
    log.warning('Предупреждение')
    log.error('Ошибка')
    log.critical('Критическая ошибка')
