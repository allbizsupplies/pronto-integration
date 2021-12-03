
from common.gui import BaseGui


class Gui(BaseGui):
    ORDER_ID_MAX_LENGTH = 7
    DISPLAY_SELECT_CUSTOMER_ACCOUNT = False
    DEFAULTS = {
        "fill_delivery_address": True,
        "select_customer_account": False,
    }

    def __init__(self, on_submit):
        super().__init__("Get Sale from EditAndPrint", on_submit)
