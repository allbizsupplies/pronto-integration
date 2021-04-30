
import unittest

from server.filemaker.client import is_valid_account_code

VALID_ACCOUNT_CODES = [
    "A04580",
    "COD0712",
    "K01547",
    "P02220",
]

INVALID_ACCOUNT_CODES = [
    None,
    "ACCOUNT",
    "CASH",
    "POS DEPOSIT",
    "COD ACCOUNT",
    "ACCPRINT",
    "WEBPRINT",
    "CASHWEB",
]

class ClientTest(unittest.TestCase):

    def test_is_valid_account_code(self):
        for account_code in VALID_ACCOUNT_CODES:
            self.assertTrue(is_valid_account_code(account_code))
        
        for account_code in INVALID_ACCOUNT_CODES:
            self.assertFalse(is_valid_account_code(account_code))
