import socket
import sys
import logging
import argparse
import select
import time
# import logs.server_log_config

from common.decorators import Log
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, RESPONDEFAULT_IP_ADDRESS, MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import get_message, send_message


server_log = logging.getLogger('server')


@Log()
def process_client_message(message, messages_list, client):

    server_log.debug(f'Обработка сообщения от клиента: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        send_message(client, {RESPONSE: 200})
        return
    elif ACTION in message and message[ACTION] == MESSAGE and TIME in message \
            and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
    else:
        send_message(client, {
            RESPONDEFAULT_IP_ADDRESS: 400,
            ERROR: 'Bad Request'
        })
        return


@Log()
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        server_log.critical(f'Попытка запуска сервера с некорректного порта {listen_port}'
                            'Порт должен быть указан в пределах от 1024 до 65535')
        sys.exit(1)
    return listen_address, listen_port


def main():

    listen_address, listen_port = arg_parser()

    server_log.info(f'Сервер запущен на порту: {listen_port}, по адресу: {listen_address}')

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)

    clients = []
    messages = []

    transport.listen(MAX_CONNECTIONS)

    while True:
        try:
            client, client_address = transport.accept()
        except OSError as err:
            print(err.errno)
            pass
        else:
            server_log.info(f'Установлено соединение с ПК {client_address}')
            clients.append(client)

        recv_data_lst = []
        send_data_lst = []

        try:
            if clients:
                recv_data_lst, send_data_lst, _ = select.select(clients, clients, [], 0)
        except OSError:
            pass

        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_message(get_message(client_with_message), messages, client_with_message)
                except:
                    server_log.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                    clients.remove(client_with_message)

        if messages and send_data_lst:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1],
            }
            del messages[0]
            for waiting_client in send_data_lst:
                try:
                    send_message(waiting_client, message)
                except:
                    server_log.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                    waiting_client.close()
                    clients.remove(waiting_client)


if __name__ == '__main__':
    main()
