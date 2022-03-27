import json
import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, RESPONDEFAULT_IP_ADDRESS, \
    ENCODING
from common.utils import send_message, get_message


class TestSocket:

    def __init__(self, test_message):
        self.test_message = test_message
        self.encoded_message = None
        self.received_message = None

    def send(self, message_to_send):
        json_test_message = json.dumps(self.test_message)
        self.encoded_message = json_test_message.encode(ENCODING)
        self.received_message = message_to_send

    def recv(self, max_len):
        json_test_message = json.dumps(self.test_message)
        return json_test_message.encode(ENCODING)


class Tests(unittest.TestCase):
    test_message_send = {ACTION: PRESENCE, TIME: 111111.111111, USER: {ACCOUNT_NAME: 'test'}}
    test_success_receive = {RESPONSE: 200}
    test_error_receive = {RESPONDEFAULT_IP_ADDRESS: 400, ERROR: 'Bad Request'}

    def test_send_message(self):
        test_socket = TestSocket(self.test_message_send)
        send_message(test_socket, self.test_message_send)
        self.assertEqual(test_socket.encoded_message, test_socket.received_message)
        # with self.assertRaises(Exception):
        #     send_message(test_socket, test_socket)

    def test_send_message_raises(self):
        test_socket = TestSocket(self.test_message_send)
        send_message(test_socket, self.test_message_send)
        self.assertRaises(TypeError, send_message, test_socket)

    def test_get_ok_message(self):
        test_sock_ok = TestSocket(self.test_success_receive)
        self.assertEqual(get_message(test_sock_ok), self.test_success_receive)

    def test_get_err_message(self):
        test_sock_err = TestSocket(self.test_error_receive)
        self.assertEqual(get_message(test_sock_err), self.test_error_receive)


if __name__ == '__main__':
    unittest.main()
