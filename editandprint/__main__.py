
from common.exceptions import SaleNotOpenException, SubmitError
from common.pronto.controller import ThinClientController
from common.settings import get_settings
from editandprint.client import WebClient
from editandprint.gui import Gui


def main():
    gui = Gui(on_submit)
    gui.show()


def on_submit(values):
    settings = get_settings("editandprint")
    controller = ThinClientController()
    try:
        controller.check_sale_open()
    except SaleNotOpenException as ex:
        raise SubmitError(str(ex))
    client = WebClient(settings)
    order = client.get_order(values["order_id"])
    controller.enter_order_id(values["order_id"])
    controller.enter_customer_reference(order["reference"])
    if values["fill_delivery_address"]:
        controller.enter_shipping_address(order["address"])
    controller.enter_line_items(order["items"])


if __name__ == "__main__":
    main()
