
from common.gui import BaseGui


class Gui(BaseGui):
    LABEL_FILL_DELIVERY_ADDRESS = "Put job name and phone number in delivery address"
    DISPLAY_SELECT_CUSTOMER_ACCOUNT = False
    ORDER_ID_MAX_LENGTH = 7
    DEFAULTS = {
        "fill_delivery_address": True,
        "select_customer_account": False,
    }

    def __init__(self, on_submit):
        super().__init__("Get Sale from FileMaker", on_submit)
