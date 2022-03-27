import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE, \
    RESPONDEFAULT_IP_ADDRESS
from server import process_client_message


class TestServer(unittest.TestCase):
    err_message = {
        RESPONDEFAULT_IP_ADDRESS: 400,
        ERROR: 'Bad Request',
    }
    succ_message = {RESPONSE: 200}

    def test_without_action(self):
        proc = process_client_message({TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}})
        self.assertEqual(proc, self.err_message)

    def test_wrong_action(self):
        proc = process_client_message({ACTION: 'Wrong', TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}})
        self.assertEqual(proc, self.err_message)

    def test_without_time(self):
        proc = process_client_message({ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}})
        self.assertEqual(proc, self.err_message)

    def test_without_user(self):
        proc = process_client_message({ACTION: PRESENCE, TIME: '1.1'})
        self.assertEqual(proc, self.err_message)

    def test_wrong_user(self):
        proc = process_client_message({ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest1'}})
        self.assertEqual(proc, self.err_message)

    def test_success_check(self):
        proc = process_client_message({ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})
        self.assertEqual(proc, self.succ_message)


if __name__ == '__main__':
    unittest.main()
