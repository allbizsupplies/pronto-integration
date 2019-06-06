
import unittest

from editandprint.order_parser import parse_order
from editandprint.order import Order


class OrderParserTest(unittest.TestCase):


    def setUp(self):
        self.dummy_html = []

        with open("./tests/dummy/response1.html") as stream:
            self.dummy_html.append(stream.read())

        with open("./tests/dummy/response2.html") as stream:
            self.dummy_html.append(stream.read())

    
    def test_parse_order(self):
        for html in self.dummy_html:
            order = parse_order(html)
            self.assertIsInstance(order, Order)
            print(order.items[1].get_pronto_format()["name"])
