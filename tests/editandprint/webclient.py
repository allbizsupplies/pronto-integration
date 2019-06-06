
import unittest
from bs4 import BeautifulSoup

from editandprint.server import get_auth, get_client
from editandprint.webclient import WebClient
from editandprint.order import Order



class WebClientTest(unittest.TestCase):

    
    def setUp(self):
        auth = {
            "username": "btreloar",
            "password": "Slartibartfast?",
        }

        self.client = WebClient(auth)
        self.client.refresh_session()
    

    def test_get_order_html(self):
        test_order_id = "59407"

        order_html = self.client.get_order_html(test_order_id)

        soup = BeautifulSoup(order_html, "html.parser")
        title = soup.title.text

        self.assertEqual(title, "Admin :: View/Update Order")

    
    def test_get_order(self):
        test_order_id = "59407"

        order = self.client.get_order(test_order_id)
        self.assertIsInstance(order, Order)

        # for item in order.items:
        #     print(item.price)

        print(order.shipping_address)
        # print(order.get_pronto_format())
