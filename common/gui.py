from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from common.exceptions import OrderNotFoundException, SubmitError, ValidationError


class BaseGui:
    LABEL_ORDER_ID = "Order ID"
    LABEL_FILL_DELIVERY_ADDRESS = "Use delivery address from order"
    LABEL_SELECT_CUSTOMER_ACCOUNT = "Automatically select the customer's account"
    DISPLAY_SELECT_CUSTOMER_ACCOUNT = True
    ORDER_ID_MAX_LENGTH = 10
    DEFAULTS = {
        "fill_delivery_address": True,
        "select_customer_account": False,
    }
    SUBMIT_BUTTON_LABEL = "Get Order"
    SUBMIT_BUTTON_LABEL_PENDING = "Getting Order..."

    def __init__(self, title, on_submit):
        self.title = title
        self.on_submit = on_submit
        self.is_pending = False

    def init_fields(self):
        self.values = {
            "order_id": StringVar(),
            "fill_delivery_address": BooleanVar(value=self.DEFAULTS["fill_delivery_address"]),
            "select_customer_account": BooleanVar(value=self.DEFAULTS["select_customer_account"]),
        }
        self.errors = {}
        for key in self.values.keys():
            self.errors[key] = StringVar()

    def process_values(self):
        values = {}
        for key, value in self.values.items():
            values[key] = value.get()
        return values

    def build(self):
        self.root = Tk()
        self.root.title(self.title)
        self.root.attributes("-topmost", True)
        top_frame = ttk.Frame(self.root, padding="3 3 12 12")
        top_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        # Add widgets.
        self.init_fields()
        order_id_frame = ttk.Frame(top_frame)
        ttk.Label(order_id_frame, text=self.LABEL_ORDER_ID).grid(
            column=1, row=1, sticky=W, padx=(0, 5))
        self.order_id = StringVar()
        self.order_id_entry = ttk.Entry(
            order_id_frame, width=20, textvariable=self.values["order_id"])
        self.order_id_entry.grid(column=2, row=1, sticky=W)
        ttk.Label(order_id_frame, textvariable=self.errors["order_id"]).grid(
            column=3, row=1, sticky=W, padx=(5, 0))
        order_id_frame.grid(column=1, row=1, sticky=W)
        self.fill_delivery_address_checkbutton = ttk.Checkbutton(top_frame, text=self.LABEL_FILL_DELIVERY_ADDRESS,
                                                                 variable=self.values["fill_delivery_address"])
        self.fill_delivery_address_checkbutton.grid(column=1, row=3, sticky=W)
        if self.DISPLAY_SELECT_CUSTOMER_ACCOUNT:
            self.select_customer_account = BooleanVar()
            self.select_customer_account_checkbutton = ttk.Checkbutton(top_frame, text=self.LABEL_SELECT_CUSTOMER_ACCOUNT,
                                                                       variable=self.values["select_customer_account"])
            self.select_customer_account_checkbutton.grid(
                column=1, row=4, sticky=W)
        self.submit_button_label = StringVar(value=self.SUBMIT_BUTTON_LABEL)
        self.submit_button = ttk.Button(
            top_frame, textvariable=self.submit_button_label, command=self.handle_submit)
        self.submit_button.grid(column=1, row=5, sticky=(W, E))
        # Add padding around widgets once all have been added.
        for child in top_frame.winfo_children():
            child.grid_configure(padx=3, pady=3)
        # Focus on Order ID Entry.
        self.order_id_entry.focus()
        # Bind keys to handlers.
        self.root.bind("<Return>", self.handle_submit)
        self.root.bind("<Escape>", self.handle_close)
        # Centre the window.
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        window_position = (
            int(screen_width / 2 - window_width / 2),
            int(screen_height / 2 - window_height / 2)
        )
        self.root.geometry("+{}+{}".format(*window_position))

    def set_pending(self, value):
        if self.is_pending == value:
            return
        self.is_pending = value
        if self.is_pending:
            self.set_inputs_state(DISABLED)
            self.submit_button_label.set(self.SUBMIT_BUTTON_LABEL_PENDING)
        else:
            self.set_inputs_state(NORMAL)
            self.submit_button_label.set(self.SUBMIT_BUTTON_LABEL)

    def set_inputs_state(self, state):
        self.order_id_entry["state"] = state
        self.fill_delivery_address_checkbutton["state"] = state
        if hasattr(self, "select_customer_account_checkbutton"):
            self.select_customer_account_checkbutton["state"] = state
        self.submit_button["state"] = state
        self.root.update()

    def show(self):
        self.build()
        self.root.mainloop()

    def handle_submit(self, keypress_event=None):
        self.set_pending(True)
        self.clear_errors()
        try:
            self.validate()
        except ValidationError as ex:
            self.set_pending(False)
            return
        try:
            self.on_submit(self.process_values())
            self.terminate()
        except SubmitError as ex:
            self.set_pending(False)
            messagebox.showerror("Error", str(ex))
        except OrderNotFoundException as ex:
            self.set_pending(False)
            messagebox.showerror("Error", str(ex))
        except Exception as ex:
            messagebox.showerror("Error", str(ex))
            self.terminate()

    def handle_close(self, keypress_event=None):
        self.terminate()

    def validate(self):
        values = self.process_values()
        errors = {}
        if len(values["order_id"]) == 0:
            errors["order_id"] = "Required"
        elif len(values["order_id"]) > self.ORDER_ID_MAX_LENGTH:
            errors["order_id"] = "Max {} characters".format(
                self.ORDER_ID_MAX_LENGTH)
        if len(errors.values()) > 0:
            self.set_errors(errors)
            raise ValidationError()

    def set_errors(self, errors):
        for key, value in errors.items():
            self.errors[key].set(value)

    def clear_errors(self):
        for key in self.errors.keys():
            self.errors[key].set("")

    def terminate(self, keypress_event=None):
        print("Terminating.")
        self.root.destroy()
