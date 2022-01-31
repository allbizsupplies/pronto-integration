
from decimal import Decimal
from datetime import date, datetime
from random import randint, choice as random_choice
import string
import time


def random_date(start=None, end=None):
    """
    Makes a random date between two given dates.
    """
    if start is None:
        start = date.fromtimestamp(100000)
    if end is None:
        end = date.today()
    return date.fromtimestamp(randint(
        int(time.mktime(start.timetuple())),
        int(time.mktime(end.timetuple()))))


def random_datetime(start=None, end=None):
    """
    Makes a random datetime between two given datetimes.
    """
    if start is None:
        start = datetime.fromtimestamp(0)
    if end is None:
        end = datetime.now()
    return datetime.fromtimestamp(randint(
        int(time.mktime(start.timetuple())),
        int(time.mktime(end.timetuple()))))


def random_order_id():
    """
    Makes a random order ID
    """
    return str(randint(100000, 999999))


def random_item_code():
    """
    Makes a random item code.
    """
    return random_string(16)


def random_price():
    """
    Makes a random price.
    """
    return Decimal(random_price_string())


def random_price_factor():
    """
    Makes a random price multiplication factor with format '0.00'.
    """
    return f"{randint(1, 5)}.{(randint(0, 19) * 5):02d}"


def random_price_string():
    """
    Makes a random price string with format '0.00'.
    """
    return f"{randint(1, 100)}.{randint(0, 99):02d}"


def random_quantity():
    """
    Makes a random quantity between 0 and 999999, inclusive.
    """
    return str(randint(0, 999999))


def random_string(length):
    """
    Makes a random string of uppercase ASCII letters.
    """
    return "".join([
        random_choice(string.ascii_uppercase) for x in range(length)])


def fake_order(values={}):
    return {
        "id": random_order_id(),
        "job_name": random_string(20),
        "contact": random_string(20),
        "reference": random_string(6),
        "job_type": "PRINT JOB",
        "status": "COMPLETED",
        "created_at": random_datetime().isoformat(timespec="seconds"),
        "due_date": random_date().isoformat(),
        "location": "COLLECTED",
    }


def fake_settings(settings={}):
    default_settings = {
        "host": random_string(10),
        "port": randint(3300, 3399),
        "dsn": random_string(10),
        "user": random_string(10),
        "password": random_string(10),
        "table": random_string(10),
        "max_connection_attempts": 10,
        "connection_attempt_delay": 30,
        "fields": {
            "id": "jobsheet number",
            "ref": "Customer Order Number",
            "job_name": "Job Name",
            "phone_number": "Ph/Mob",
            "account_code": "Payment method",
            "contact": "Contact",
            "email": "email",
            "delivery_address": "Deliver",
            "created_at": "Date taken",
            "due_date": "Due Date",
            "job_type": "JOB QUOTE SHEET",
            "job_part_number": "PART",
            "job_part_count": "PART OF",
            "status": "JOB COMPLETED",
            "location": "JOB LOCATION",
            "items": [
                {
                    "code": "Varience Item code 1",
                    "description": "Varience details",
                    "quantity": "Varience Item code QTY 1",
                    "unit_price": "Unit price 1"
                },
                {
                    "code": "Varience Item code 2",
                    "description": "Varience details Copy",
                    "quantity": "Varience Item code QTY 2",
                    "unit_price": "Unit price 2"
                },
                {
                    "code": "Varience Item code 3",
                    "description": "Varience details Copy2",
                    "quantity": "Varience Item code QTY 3",
                    "unit_price": "Unit price 3"
                },
                {
                    "code": "Varience Item code 4",
                    "description": "Varience details Copy3",
                    "quantity": "Varience Item code QTY 4",
                    "unit_price": "Unit price 4"
                },
                {
                    "code": "Varience Item code 5",
                    "description": "Varience details Copy4",
                    "quantity": "Varience Item code QTY 5",
                    "unit_price": "Unit price 5"
                },
                {
                    "code": "Varience Item code 6",
                    "description": "Varience details Copy5",
                    "quantity": "Varience Item code QTY 6",
                    "unit_price": "Unit price 6"
                },
                {
                    "code": "Varience Item code 7",
                    "description": "Varience details Copy6",
                    "quantity": "Varience Item code QTY 7",
                    "unit_price": "Unit price 7"
                },
                {
                    "code": "Varience Item code 8",
                    "description": "Varience details Copy7",
                    "quantity": "Varience Item code QTY 8",
                    "unit_price": "Unit price 8"
                },
                {
                    "code": "Varience Item code 9",
                    "description": "Varience details Copy8",
                    "quantity": "Varience Item code QTY 9",
                    "unit_price": "Unit price 9"
                },
                {
                    "code": "Varience Item code 10",
                    "description": "Varience details Copy9",
                    "quantity": "Varience Item code QTY 10",
                    "unit_price": "Unit price 10"
                }
            ],
            "art": [
                {
                    "description": "Varience details Art 1",
                    "quantity": "Varience details Art Time",
                    "price": "Varience details Art cost"
                },
                {
                    "description": "Varience details Art 2",
                    "quantity": "Varience details Art Time 2",
                    "price": "Varience details Art cost 2"
                },
                {
                    "description": "Varience details Art 3",
                    "quantity": "Varience details Art Time 3",
                    "price": "Varience details Art cost 3"
                },
                {
                    "description": "Varience details Art 4",
                    "quantity": "Varience details Art Time 4",
                    "price": "Varience details Art cost 4"
                },
                {
                    "description": "Varience details Art 5",
                    "quantity": "Varience details Art Time 5",
                    "price": "Varience details Art cost 5"
                },
                {
                    "description": "Varience details Art 6",
                    "quantity": "Varience details Art Time 6",
                    "price": "Varience details Art cost 6"
                },
                {
                    "description": "Varience details Art 7",
                    "quantity": "Varience details Art Time 7",
                    "price": "Varience details Art cost 7"
                },
                {
                    "description": "Varience details Art 8",
                    "quantity": "Varience details Art Time 8",
                    "price": "Varience details Art cost 8"
                },
                {
                    "description": "Varience details Art 9",
                    "quantity": "Varience details Art Time 9",
                    "price": "Varience details Art cost 9"
                },
                {
                    "description": "Varience details Art 10",
                    "quantity": "Varience details Art Time 10",
                    "price": "Varience details Art cost 10"
                },
                {
                    "description": "Varience details Art 11",
                    "quantity": "Varience details Art Time 11",
                    "price": "Varience details Art cost 11"
                },
                {
                    "description": "Varience details Art 12",
                    "quantity": "Varience details Art Time 12",
                    "price": "Varience details Art cost 12"
                },
                {
                    "description": "Varience details Art 13",
                    "quantity": "Varience details Art Time 13",
                    "price": "Varience details Art cost 13"
                },
                {
                    "description": "Varience details Art 14",
                    "quantity": "Varience details Art Time 14",
                    "price": "Varience details Art cost 14"
                },
                {
                    "description": "Varience details Art 15",
                    "quantity": "Varience details Art Time 15",
                    "price": "Varience details Art cost 15"
                }
            ],
            "payments": [
                {
                    "amount": "payed ammount",
                    "invoice": "Invoice Number"
                },
                {
                    "amount": "payed ammount Copy",
                    "invoice": "Invoice Number Copy"
                }
            ]
        }
    }
    default_settings.update(settings)
    return default_settings
