import argparse
import sys
import json
import socket
import time
import logging
# import logs.client_log_config
from common.decorators import Log
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import get_message, send_message
from errors import ServerError, ReqFieldMissingError

client_log = logging.getLogger('client')


@Log()
def message_from_server(message):
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        print(f'Получено сообщение от пользователя '
              f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        client_log.info(f'Получено сообщение от пользователя '
                        f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        client_log.error(f'Получено некорректное сообщение от сервера: {message}')


@Log()
def create_message(sock, account_name='Guest'):

    message = input('Введите сообщение для отправки или \'!!!\' для завершения работы: ')
    if message == '!!!':
        sock.close()
        client_log.info('Завершение работы по команде пользователя.')
        print('Спасибо за использование нашего сервиса!')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message,
    }
    client_log.debug(f'Сформирован словарь сообщения: {message_dict}')
    return message_dict


@Log()
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


@Log()
def process_response_ans(message):
    client_log.info(f'Обработка сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            client_log.info('Успешная обработка сообшения от сервера.')
            return '200 : OK'
        client_log.critical('Не успешная обработка сообщения от сервера.')
        return f'400 : {message[ERROR]}'
    raise ValueError


@Log()
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    if not 1023 < server_port < 65536:
        client_log.critical('Порт должен быть указан в пределах от 1024 до 65535')
        sys.exit(1)

    if client_mode not in ('listen', 'send'):
        client_log.critical(f'Указан недопустимый режим работы {client_mode}')
        sys.exit(1)

    return server_address, server_port, client_mode


def main():

    server_address, server_port, client_mode = arg_parser()

    client_log.info(f'Запущен клиент с параметрами: адрес сервера: {server_address}, '
                    f'порт: {server_port}, режим работы: {client_mode}')
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence())
        answer = process_response_ans(get_message(transport))
        print(client_mode)
        client_log.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
    except json.JSONDecodeError:
        client_log.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ServerError as err:
        client_log.error(f'При установке соединения сервер вернул ошибку: {err.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_err:
        client_log.error(f'В ответе сервера отсутствует необходимое поле: {missing_err.missing_field}')
        sys.exit(1)
    except ConnectionRefusedError:
        client_log.critical(f'Не удалось подключится к серверу {server_address}:{server_port}, '
                            f'конечный компьютер отверг запрос на подключение')
        sys.exit(1)
    else:
        if client_mode == 'send':
            print('=== Режим работы - отправка сообщений. ===')
        else:
            print('=== Режим работы - приём сообщений. ===')

        while True:
            print(client_mode)
            if client_mode == 'send':
                try:
                    send_message(transport, create_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    client_log.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)

            if client_mode == 'listen':
                try:
                    message_from_server(get_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    client_log.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)


if __name__ == '__main__':
    main()
