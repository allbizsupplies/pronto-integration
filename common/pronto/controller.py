
from ahk import AHK
import os
from time import sleep

from common.exceptions import ProntoStatusBarException, ProntoStatusException, SaleNotOpenException

SCRIPT_DIR = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "scripts")

WAIT_DURATION = 1
WAIT_INTERVAL = 0.05

POS_READY = "Confirm Operator Password"
POS_READY_FOR_ITEM = "Enter Item Code [HELP], Hotkey or '.' for Options"
POS_READY_FOR_NOTE = "Press the ESC key to finish (or Save/Cancel)"
POS_READY_FOR_QUANTITY = ""
POS_READY_FOR_PRICE = "Enter the item price"
POS_SAVE_NOTE = "Save your changes"
POS_CORRECT = "Correct values on the screen"
POS_READY_FOR_ADDR_LINE = "Enter the delivery address/instr. line"
POS_READY_FOR_ADDR_POSTCODE = "Enter the postcode for this address"
POS_READY_FOR_ADDR_PHONE = "Enter the delivery Phone number"
POS_READY_FOR_ADDR_FAX = "Enter the delivery Fax number"
POS_READY_FOR_ADDR_DPID = "Enter the delivery point identifier"
POS_READY_FOR_ADDR_DATE = "Enter the estimated delivery date for this order"
POS_READY_FOR_CUS_REF = "Enter the customer order no"

ahk = AHK()


def run_script(name, **kwargs):
    with open(os.path.join(SCRIPT_DIR, name + ".ahk")) as file:
        script = file.read()
    return ahk.run_script(script.format(**kwargs))


class ThinClientController:
    _window = None
    _statusbar_classname = None

    def __init__(self, company_name="Allbiz Supplies Pty. Ltd."):
        self.window_title = company_name
        self.company_name = company_name

    @property
    def window(self):
        if self._window is None:
            self._window = ahk.win_get(title=self.window_title)
        return self._window

    @property
    def statusbar_classname(self):
        if self._statusbar_classname is None:
            self.window.activate()
            win_x_pos, win_y_pos, win_width, win_height = self.window.rect
            orig_pos = ahk.mouse_position
            ahk.mouse_move(win_x_pos + 28, win_y_pos +
                           win_height - 15, speed=0)
            _statusbar_classname = run_script("classname_from_mouse")
            ahk.mouse_move(*orig_pos, speed=0)
            if _statusbar_classname[:13] != "Afx:StatusBar":
                raise ProntoStatusBarException()
            self._statusbar_classname = _statusbar_classname
        return self._statusbar_classname

    @property
    def status(self):
        return self.get_text(self.statusbar_classname)

    def enter_order_id(self, order_id):
        self.send_on_status("DN{Enter}", POS_READY_FOR_ITEM)
        self.send_raw_on_status("Order ID: " + order_id, POS_READY_FOR_NOTE)
        self.send_on_status("{Esc}", POS_READY_FOR_NOTE)
        self.send_on_status("S", POS_SAVE_NOTE)

    def enter_line_items(self, line_items):
        self.focus_window()
        for line_item in line_items:
            self.enter_line_item(line_item)

    def enter_line_item(self, line_item):
        self.wait_for_status(POS_READY_FOR_ITEM)
        # Enter the item code.
        self.send_raw_on_status(line_item["item_code"], POS_READY_FOR_ITEM)
        self.send_on_status("{Enter}", POS_READY_FOR_ITEM)
        # Enter the item quantity.
        if line_item["quantity"]:
            self.send_on_status("*{Enter}", POS_READY_FOR_ITEM)
            self.send_raw_on_status(
                line_item["quantity"], POS_READY_FOR_QUANTITY)
            self.send_on_status("{Enter 3}", POS_READY_FOR_QUANTITY)
        # Enter the item price.
        if line_item["price"]:
            self.send_on_status("P{Enter}", POS_READY_FOR_ITEM)
            self.send_raw_on_status(line_item["price"], POS_READY_FOR_PRICE)
            self.send_on_status("{Enter 3}", POS_READY_FOR_PRICE)
        # Enter the description as a note.
        if "name" or "description" in line_item.keys():
            self.send_on_status("DN{Enter}", POS_READY_FOR_ITEM)
            if "name" in line_item.keys():
                self.send_raw_on_status(
                    "Name: " + line_item["name"], POS_READY_FOR_NOTE)
                self.send_raw_on_status("`n", POS_READY_FOR_NOTE)
            if "description" in line_item.keys():
                self.send_raw_on_status(
                    line_item["description"], POS_READY_FOR_NOTE)
        self.send_on_status("{Esc}", POS_READY_FOR_NOTE)
        self.send_on_status("S", POS_SAVE_NOTE)

    def enter_customer_reference(self, reference):
        self.send_on_status("REF{Enter}", POS_READY_FOR_ITEM)
        self.send_on_status(reference, POS_READY_FOR_CUS_REF)
        self.send_on_status("{Enter}", POS_READY_FOR_CUS_REF)

    def select_customer_account(self, account_code):
        self.send_on_status("CUS-", POS_READY_FOR_ITEM)
        self.send_on_status(account_code, POS_READY_FOR_ITEM)
        self.send_on_status("{Enter}", POS_READY_FOR_ITEM)

    def enter_shipping_address(self, address):
        self.send_on_status("DA{Enter}", POS_READY_FOR_ITEM)
        self.send_on_status("C", POS_CORRECT)
        self.send_on_status(address["name"], POS_READY_FOR_ADDR_LINE)
        self.send_on_status("{Enter}", POS_READY_FOR_ADDR_LINE)
        self.send_on_status(address["address_1"], POS_READY_FOR_ADDR_LINE)
        self.send_on_status("{Enter}", POS_READY_FOR_ADDR_LINE)
        self.send_on_status(address["address_2"], POS_READY_FOR_ADDR_LINE)
        self.send_on_status("{Enter}", POS_READY_FOR_ADDR_LINE)
        self.send_on_status(address["address_3"], POS_READY_FOR_ADDR_LINE)
        self.send_on_status("{Enter 4}{Esc}", POS_READY_FOR_ADDR_LINE)
        self.send_on_status(address["postcode"], POS_READY_FOR_ADDR_POSTCODE)
        self.send_on_status("{Enter}", POS_READY_FOR_ADDR_POSTCODE)
        self.send_on_status(address["phone"], POS_READY_FOR_ADDR_PHONE)
        self.send_on_status("{F4}", POS_READY_FOR_ADDR_PHONE)

    def check_sale_open(self):
        self.focus_window()
        attempts = 0
        while(attempts < 4):
            if (self.status == POS_READY_FOR_ITEM):
                return
            attempts += 1
            sleep(0.25)
            self.send_input("{Enter}")
        raise SaleNotOpenException()

    def wait_for_status(self, expected_status):
        time_waited = 0
        while(time_waited < WAIT_DURATION):
            if self.status == expected_status:
                return
            sleep(WAIT_INTERVAL)
            time_waited += WAIT_INTERVAL
        raise ProntoStatusException(expected_status, self.status)

    def send_on_status(self, value, expected_status):
        self.wait_for_status(expected_status)
        self.send_input(str(value))

    def send_raw_on_status(self, value, expected_status):
        self.wait_for_status(expected_status)
        self.send_raw(str(value))

    def send_input(self, value):
        ahk.send_input(value)

    def send_raw(self, value):
        ahk.send_raw(value)

    def get_text(self, classname):
        return run_script(
            "text_from_classname",
            classname=classname,
            window_title=self.window_title)

    def focus_window(self):
        self.window.activate()
