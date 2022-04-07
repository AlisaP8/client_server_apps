import socket
import sys
import json
import logging
import logs.server_log_config
from common.decorators import Log
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, RESPONDEFAULT_IP_ADDRESS
from common.utils import get_message, send_message


server_log = logging.getLogger('server')


@Log()
def process_client_message(message):

    server_log.debug(f'Обработка сообщения от клиента: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONDEFAULT_IP_ADDRESS: 400,
        ERROR: 'Bad Request'
    }


def main():

    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if not 65535 >= listen_port >= 1024:
            raise ValueError
    except IndexError:
        server_log.critical(f'После параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        server_log.critical(f'Попытка запуска сервера с некорректного порта {listen_port}.'
                            'Порт должен быть указан в пределах от 1024 до 65535')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''

    except IndexError:
        server_log.critical('После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
        sys.exit(1)

    server_log.info(f'Сервер запущен на порту: {listen_port}.')

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))

    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        server_log.info(f'Установлено соедение с {client_address}')
        try:
            message_from_client = get_message(client)
            server_log.debug(f'Получено сообщение {message_from_client}')
            response = process_client_message(message_from_client)
            server_log.info(f'Cформирован ответ клиенту {response}')
            send_message(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            server_log.critical('Принято некорретное сообщение от клиента')
            client.close()


if __name__ == '__main__':
    main()
