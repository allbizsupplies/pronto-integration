
from common.exceptions import SaleNotOpenException, SubmitError
from common.pronto.controller import ThinClientController
from common.settings import get_settings
from filemaker.client import ODBCClient
from filemaker.gui import Gui


def main():
    gui = Gui(on_submit)
    gui.show()


def on_submit(values):
    settings = get_settings("filemaker")
    controller = ThinClientController()
    try:
        controller.check_sale_open()
    except SaleNotOpenException as ex:
        raise SubmitError(str(ex))
    client = ODBCClient(settings)
    order_id = values["order_id"]
    order = client.get_order(order_id)
    controller.enter_order_id(f"FM-{order_id}")
    controller.enter_customer_reference(order["reference"])
    if values["fill_delivery_address"]:
        address = build_address(order)
        controller.enter_shipping_address(address)
    controller.enter_line_items(order["items"])


def build_address(order):
    address = {
        "name": order["job_name"][:30].strip(),
        "address_1": "",
        "address_2": "",
        "address_3": "",
        "address_4": "",
        "phone": "",
        "postcode": "",
    }
    if order["phone_number"]:
        order["address_1"] = order["phone_number"][:30]
        order["phone"] = order["phone_number"][:15]
    return address


if __name__ == "__main__":
    main()
