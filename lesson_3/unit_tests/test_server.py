import unittest
from lesson_3.common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from lesson_3.server import process_client_message


class TestServer(unittest.TestCase):
    err_message = {
        RESPONSE: 400,
        ERROR: 'Bad Request',
    }
    succ_message = {RESPONSE: 200}

    def test_without_action(self):
        self.assertEqual(process_client_message(
            {TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}),
            self.err_message)

    def test_wrong_action(self):
        self.assertEqual(process_client_message(
            {ACTION: 'Wrong', TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}),
            self.err_message)

    def test_without_time(self):
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}),
            self.err_message)








