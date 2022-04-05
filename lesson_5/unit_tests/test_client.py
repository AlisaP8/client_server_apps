import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR
from client import create_presence, process_ans


class TestClient(unittest.TestCase):

    def test_presence(self):
        test = create_presence()
        test[TIME] = 1.1
        out = {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}
        self.assertEqual(test, out)

    def test_correct_answer(self):
        ans = process_ans({RESPONSE: 200})
        self.assertEqual(ans, '200 : OK')

    def test_bad_request(self):
        ans = process_ans({RESPONSE: 400, ERROR: 'Bad Request'})
        self.assertEqual(ans, '400 : Bad Request')

    def test_no_response(self):
        self.assertRaises(ValueError, process_ans, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
