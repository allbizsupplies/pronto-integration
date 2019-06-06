import unittest
from bs4 import BeautifulSoup
from datetime import date
from decimal import Decimal
from random import randint

from editandprint.order import Order, Item, ItemOption, ShippingAddress



class OrderTestCase(unittest.TestCase):


    def get_dummy_address(self):
        return ShippingAddress(
            contact_name = "Dummy Contact Name",
            contact_email = "dummay@example.com",
            street = "Level 1, Dummy Street",
            suburb = "Dummy Suburb",
            state = "Dummy State",
            postcode = "1234",
            country = "Dummy Country",
            contact_phone = "12345678",
            company_name = "Dummy Company Name"
        )


    def get_dummy_items(self):
        items = []

        for i in range(2):
            items.append(Item(
                item_code = "ALL-DUMMY" + str(i),
                label = "Dummy Item #" + str(i),
                quantity = str(randint(50, 1000)),
                price = Decimal(randint(5000, 10000) / Decimal(100)),
                options = self.get_dummy_options()
            ))

        return items


    def get_dummy_options(self):
        options = []

        for i in range(randint(0, 4)):
            options.append(ItemOption(
                key = "Dummy Key #" + str(i),
                value = "Dummy Value" if randint(0, 1) else None
            ))

        return options


    def get_dummy_order(self):
        return Order(
            shipping_address = self.get_dummy_address(),
            items = self.get_dummy_items()
        )


    def test_get_pronto_format(self):
        order = self.get_dummy_order()

        data = order.get_pronto_format()
        self.assertIsInstance(data, dict)

        for item in data["items"]:
            print(item)
