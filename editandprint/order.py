
from decimal import Decimal
from string import Template


class Entity:
    pass


class Item(Entity):

    def __init__(self,
                 item_code=None,
                 label=None,
                 name=None,
                 quantity=None,
                 price=None,
                 options=None
                 ):
        self.item_code = item_code
        self.label = label
        self.name = name
        self.quantity = quantity
        self.price = price
        self.options = options if options else []
        self.options = options if options else []

    def get_pronto_format(self):
        data = {
            "item_code": self.item_code,
            "name": self.name,
            "description": self.label,
            "quantity": str(self.quantity),
            "price": str(formatted_price(self.price)),
        }

        data["options"] = []
        for option in self.options:
            option_data = option.get_pronto_format()
            if option_data:
                data["options"].append(option_data)

        return data


class ItemOption(Entity):

    def __init__(self,
                 key=None,
                 value=None,
                 ):
        self.key = key
        self.value = value

    def get_pronto_format(self):
        return {
            "key": self.key,
            "value": self.value,
        }


class Order(Entity):

    def __init__(self,
                 shipping_address=None,
                 items=[]
                 ):
        self.shipping_address = shipping_address
        self.items = items

    def get_pronto_format(self):
        data = {}

        data["address"] = self.shipping_address.get_pronto_format()

        data["items"] = []
        for item in self.items:
            data["items"].append(item.get_pronto_format())

        return data


class ShippingAddress(Entity):

    def __init__(self,
                 contact_name=None,
                 contact_email=None,
                 street=None,
                 suburb=None,
                 state=None,
                 postcode=None,
                 country=None,
                 contact_phone=None,
                 company_name=None
                 ):

        self.contact_name = contact_name
        self.contact_email = contact_email
        self.street = street
        self.suburb = suburb
        self.state = state
        self.postcode = postcode
        self.country = country
        self.contact_phone = contact_phone
        self.company_name = company_name

    def get_pronto_format(self):
        address_name = None
        if self.company_name:
            address_name = self.company_name[:30]
        elif self.contact_name:
            address_name = self.contact_name[:30]

        attention_note = None
        if self.company_name:
            attention_note = "ATTN: " + self.contact_name[:24]

        return {
            "name": address_name,
            "address_1": self.street[:30],
            "address_2": self.suburb[:30],
            "address_3": self.state[:30],
            "address_4": attention_note,
            "phone": self.contact_phone[:15],
            "postcode": self.postcode,
        }


def formatted_price(price):
    if price:
        return round(price * Decimal(1.1), 4)
