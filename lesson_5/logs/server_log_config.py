import os
import sys
import logging.handlers
sys.path.append('../')

server_formatter = logging.Formatter('%(asctime)-25s %(levelname)-10s %(filename)-22s %(message)s')

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

stream_hand = logging.StreamHandler()
stream_hand.setFormatter(server_formatter)
stream_hand.setLevel(logging.ERROR)
log_file = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf-8', interval=1, when='D')
log_file.setFormatter(server_formatter)

log = logging.getLogger('server')
log.addHandler(stream_hand)
log.addHandler(log_file)
log.setLevel(logging.DEBUG)

if __name__ == '__main__':
    log.debug('Отладочная информация')
    log.info('Информационное сообщение')
    log.warning('Предупреждение')
    log.error('Ошибка')
    log.critical('Критическая ошибка')
