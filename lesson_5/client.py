import sys
import json
import socket
import time
import logging
import logs.client_log_config
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from common.utils import get_message, send_message


client_log = logging.getLogger('client')


def create_presence(account_name='Guest'):

    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    client_log.debug(f'Создание {PRESENCE} сообщения для пользователя {account_name}.')
    return out


def process_ans(message):
    client_log.info(f'Обработка сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            client_log.info('Успешная обработка сообшения от сервера.')
            return '200 : OK'
        client_log.critical('Не успешная обработка сообщения от сервера.')
        return f'400 : {message[ERROR]}'
    raise ValueError


def main():

    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if not 65535 >= server_port >= 1024:
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        client_log.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}.'
            f'Порт должен быть указан в пределах от 1024 до 65535.')
        sys.exit(1)

    client_log.info(f'Запущен клиент с парамертами: '
                    f'адрес сервера: {server_address}, порт: {server_port}')

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((server_address, server_port))

    message_to_server = create_presence()
    client_log.info('Отправка сообшения серверу.')
    send_message(transport, message_to_server)
    try:
        answer = process_ans(get_message(transport))
        client_log.info(f'Принят ответ от сервера {answer}')

    except (ValueError, json.JSONDecodeError):
        client_log.critical('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    main()
