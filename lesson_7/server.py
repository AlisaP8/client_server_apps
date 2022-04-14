import socket
import sys
import logging
import argparse
import select
import time
import logs.server_log_config

from common.decorators import Log
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, RESPONDEFAULT_IP_ADDRESS, MESSAGE, MESSAGE_TEXT, SENDER, DESTINATION, \
    EXIT
from common.utils import get_message, send_message


server_log = logging.getLogger('server')


@Log()
def process_client_message(message, messages_list, client, clients, names):

    server_log.debug(f'Обработка сообщения от клиента: {message}')

    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message:

        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, {RESPONSE: 200})
        else:
            response = RESPONDEFAULT_IP_ADDRESS
            response[ERROR] = 'Имя пользователя уже занято.'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    elif ACTION in message and message[ACTION] == MESSAGE and \
            DESTINATION in message and TIME in message \
            and SENDER in message and MESSAGE_TEXT in message:
        messages_list.append(message)
        return
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    else:
        response = RESPONDEFAULT_IP_ADDRESS
        response[ERROR] = 'Запрос некорректен.'
        send_message(client, response)
        return


@Log()
def process_message(message, names, listen_socks):
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        server_log.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                        f'от пользователя {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        server_log.error(f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
                         'отправка сообщения невозможна.')


@Log()
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        server_log.critical(
            f'Попытка запуска сервера с некорректного порта {listen_port}'
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

    names = dict()

    transport.listen(MAX_CONNECTIONS)

    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
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
                    process_client_message(get_message(client_with_message),
                                           messages, client_with_message, clients, names)
                except:
                    server_log.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                    clients.remove(client_with_message)

        for i in messages:
            try:
                process_message(i, names, send_data_lst)
            except Exception:
                server_log.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                clients.remove(names[i[DESTINATION]])
                del names[i[DESTINATION]]
        messages.clear()


        # if messages and send_data_lst:
        #     message = {
        #         ACTION: MESSAGE,
        #         SENDER: messages[0][0],
        #         TIME: time.time(),
        #         MESSAGE_TEXT: messages[0][1],
        #     }
        #     del messages[0]
        #     for waiting_client in send_data_lst:
        #         try:
        #             send_message(waiting_client, message)
        #         except:
        #             server_log.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
        #             waiting_client.close()
        #             clients.remove(waiting_client)


if __name__ == '__main__':
    main()
