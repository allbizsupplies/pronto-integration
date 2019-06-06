
import unittest

from editandprint.server import get_auth, get_client
from editandprint.webclient import WebClient


class ServerTest(unittest.TestCase):

    
    def setUp(self):
        self.auth = {
            "username": "btreloar",
            "password": "Slartibartfast?",
        }

        self.settings = {
            "host": "abs-srv3",
            "port": 3301,
        }

    
    def test_get_client(self):
        client = get_client(self.auth)
        self.assertIsInstance(client, WebClient)
        