import argparse
import sys
import json
import socket
import threading
import time
import logging
import logs.client_log_config
from common.decorators import Log
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, SENDER, EXIT, DESTINATION
from common.utils import get_message, send_message
from errors import ServerError, ReqFieldMissingError, IncorrectDataRecivedError

client_log = logging.getLogger('client')


def print_help():
    print('Поддерживаемые команды:')
    print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


@Log()
def create_exit_message(account_name):
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
    }


@Log()
def message_from_server(sock, my_username):
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and DESTINATION in message \
                    and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                print(f'Получено сообщение от пользователя '
                      f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                client_log.info(f'Получено сообщение от пользователя '
                                f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
            else:
                client_log.error(f'Получено некорректное сообщение от сервера: {message}')
        except IncorrectDataRecivedError:
            client_log.error('Не удалось декодировать полученное сообщение.')
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
            client_log.critical('Потеряно соединение с сервером.')
            break


@Log()
def create_message(sock, account_name='Guest'):

    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение для отправки: ')
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message,
    }
    client_log.debug(f'Сформирован словарь сообщения: {message_dict}')
    try:
        send_message(sock, message_dict)
        client_log.info(f'Отправлено сообщение для пользователя {to_user}')
    except:
        client_log.critical('Потеряно соединение с сервером.')
        sys.exit(1)


@Log()
def user_interactive(sock, username):
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'message' or command == 'm':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_exit_message(username))
            print('Завершение соединения.')
            client_log.info('Завершение работы по команде пользователя.')
            time.sleep(0.5)
            break
        else:
            print('Команда не распознана, попробуйте снова. help - вывести поддерживаемые команды.')


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
    parser.add_argument('-n', '--name', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        client_log.critical('Порт должен быть указан в пределах от 1024 до 65535')
        sys.exit(1)

    return server_address, server_port, client_name


def main():

    server_address, server_port, client_name = arg_parser()

    print(f'Консольный месседжер. Клиентский модуль. Имя пользователя: {client_name}')

    if not client_name:
        client_name = input('Введите имя пользователя: ')

    client_log.info(f'Запущен клиент с параметрами: адрес сервера: {server_address}, '
                    f'порт: {server_port}, режим работы: {client_name}')
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
        answer = process_response_ans(get_message(transport))
        client_log.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print('Установлено соединение с сервером.')
    except json.JSONDecodeError:
        client_log.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ServerError as err:
        client_log.error(f'При установке соединения сервер вернул ошибку: {err.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_err:
        client_log.error(f'В ответе сервера отсутствует необходимое поле: {missing_err.missing_field}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        client_log.critical(
            f'Не удалось подключится к серверу {server_address}:{server_port}, '
            f'Конечный компьютер отверг запрос на подключение')
        sys.exit(1)
    else:
        receiver = threading.Thread(target=message_from_server, args=(transport, client_name), daemon=True)
        receiver.start()

        user_interface = threading.Thread(target=user_interactive, args=(transport, client_name), daemon=True)
        user_interface.start()
        client_log.debug('Запущены процессы')

        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


        # if client_mode == 'send':
        #     print('=== Режим работы - отправка сообщений. ===')
        # else:
        #     print('=== Режим работы - приём сообщений. ===')
        #
        # while True:
        #     print(client_mode)
        #     if client_mode == 'send':
        #         try:
        #             send_message(transport, create_message(transport))
        #         except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
        #             client_log.error(f'Соединение с сервером {server_address} было потеряно.')
        #             sys.exit(1)
        #
        #     if client_mode == 'listen':
        #         try:
        #             message_from_server(get_message(transport))
        #         except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
        #             client_log.error(f'Соединение с сервером {server_address} было потеряно.')
        #             sys.exit(1)


if __name__ == '__main__':
    main()
