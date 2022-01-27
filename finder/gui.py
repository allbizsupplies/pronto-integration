
from datetime import date, datetime
from queue import Queue
from tkinter import messagebox, Tk, ttk, StringVar, N, S, E, W
import tkinter

from common.exceptions import OrderNotFoundException, SubmitError, ValidationError


class Gui():
    LABEL_QUERY = "Enter search terms"
    SUBMIT_BUTTON_LABEL = "Search"
    SUBMIT_BUTTON_LABEL_PENDING = "Searching..."
    QUERY_MAX_LENGTH = 1023

    TABLE_COLUMNS = [
        {
            "key": "id",
            "heading": "ID",
            "width": 100,
            "anchor": W,
        },
        {
            "key": "job_name",
            "heading": "Job Name",
            "width": 300,
            "anchor": W,
        },
        {
            "key": "contact",
            "heading": "Contact",
            "width": 200,
            "anchor": W,
        },
        {
            "key": "job_type",
            "heading": "Job Type",
            "width": 120,
            "anchor": W,
        },
        {
            "key": "status",
            "heading": "Status",
            "width": 100,
            "anchor": W,
        },
        {
            "key": "created_at",
            "heading": "Created",
            "width": 80,
            "anchor": W,
            "type": "datetime",
        },
        {
            "key": "due_date",
            "heading": "Due Date",
            "width": 80,
            "anchor": W,
            "type": "date",
        },
        {
            "key": "location",
            "heading": "Location",
            "width": 160,
            "anchor": W,
        }
    ]

    def __init__(self, title, on_submit_search, on_mark_order_collected):
        self.title = title
        self.on_submit_search = on_submit_search
        self.on_mark_order_collected = on_mark_order_collected
        self.is_pending = False

    def init_fields(self):
        self.values = {
            "query": StringVar(),
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
        top_frame = ttk.Frame(self.root, padding="3 3 12 12")
        top_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Add search bar widgets.
        self.init_fields()
        query_frame = ttk.Frame(top_frame)
        ttk.Label(query_frame, text=self.LABEL_QUERY).grid(
            column=0, row=0, sticky=W, padx=(0, 5))
        self.query = StringVar()
        self.query_entry = ttk.Entry(
            query_frame, width=40, textvariable=self.values["query"])
        self.query_entry.grid(column=1, row=0, sticky=W)
        self.submit_button_label = StringVar(value=self.SUBMIT_BUTTON_LABEL)
        self.submit_button = ttk.Button(
            query_frame,
            textvariable=self.submit_button_label,
            width=20,
            command=self.handle_submit)
        self.submit_button.grid(column=2, row=0, sticky=(W))
        query_frame.grid(column=0, row=0, sticky=W)

        def on_select_tree(event):
            item_id = event.widget.focus()
            if item_id:
                item = event.widget.item(item_id)
                values = item['values']
                order_id = values[0]
                self.handle_mark_order_collected(order_id)

        # Add table widget.
        table_frame = ttk.Frame(top_frame)
        self.tree = ttk.Treeview(
            table_frame,
            selectmode="browse",
            show="headings",
            height=20)
        self.tree.grid(column=0, row=0)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                  command=self.tree.yview)
        scrollbar.grid(column=1, row=0, sticky=(N, S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree["columns"] = [col["key"] for col in self.TABLE_COLUMNS]
        self.tree.bind("<Double-Button-1>", on_select_tree)
        self.tree.bind("<Return>", on_select_tree)
        for col in self.TABLE_COLUMNS:
            self.tree.column(
                col["key"],
                width=col["width"],
                anchor=col["anchor"],
                stretch=col.get("stretch", False))
            self.tree.heading(col["key"], text=col["heading"])
        table_frame.grid(column=0, row=1, sticky=W)

        # Add padding around widgets once all have been added.
        for child in top_frame.winfo_children():
            child.grid_configure(padx=3, pady=3)

        # Focus on Order ID Entry.
        self.query_entry.focus()

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
            int(screen_height / 2 - window_height / 2))
        self.root.geometry("+{}+{}".format(*window_position))

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for order in self.orders:
            values = []
            for col in self.TABLE_COLUMNS:
                value = order[col["key"]]
                if value and col.get("type") == "datetime":
                    value = datetime.fromisoformat(value).strftime("%d-%m-%Y")
                if value and col.get("type") == "date":
                    value = date.fromisoformat(value).strftime("%d-%m-%Y")
                values.append(value)
            self.tree.insert("", "end", values=values)

    def show(self):
        self.build()
        self.root.mainloop()

    def handle_mark_order_collected(self, order_id):
        self.set_pending(True)
        proceed = messagebox.askyesno(
            title='Confirmation',
            message='Mark order as collected?')
        if proceed:
            try:
                pass
                data = self.on_mark_order_collected(order_id)
                orders = self.orders
                for index, order in enumerate(orders):
                    if order['id'] == order_id:
                        orders[index] = data["order"]
                self.set_orders(orders)
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
                self.terminate()
        self.set_pending(False)

    def handle_submit(self, keypress_event=None):
        self.clear_errors()
        try:
            self.validate()
        except ValidationError as ex:
            return
        self.set_pending(True)
        try:
            values = self.process_values()
            data = self.on_submit_search(values["query"])
            self.set_orders(data["orders"])
        except SubmitError as ex:
            messagebox.showerror("Error", str(ex))
        except Exception as ex:
            messagebox.showerror("Error", str(ex))
            self.terminate()
        self.set_pending(False)

    def handle_close(self, keypress_event=None):
        self.terminate()

    def validate(self):
        values = self.process_values()
        errors = {}
        if len(values["query"]) == 0:
            errors["query"] = "Required"
        elif len(values["query"]) > self.QUERY_MAX_LENGTH:
            errors["query"] = f"Max {self.QUERY_MAX_LENGTH} characters"
        if len(errors.values()) > 0:
            self.set_errors(errors)
            raise ValidationError()

    def set_orders(self, orders):
        self.orders = orders
        self.refresh_table()

    def set_pending(self, value):
        if self.is_pending == value:
            return
        self.is_pending = value
        if self.is_pending:
            self.submit_button_label.set(self.SUBMIT_BUTTON_LABEL_PENDING)
            self.set_inputs_state(tkinter.DISABLED)
        else:
            self.set_inputs_state(tkinter.NORMAL)
            self.submit_button_label.set(self.SUBMIT_BUTTON_LABEL)

    def set_inputs_state(self, state):
        self.query_entry["state"] = state
        self.submit_button["state"] = state
        self.root.update()

    def set_errors(self, errors):
        for key, value in errors.items():
            self.errors[key].set(value)

    def clear_errors(self):
        for key in self.errors.keys():
            self.errors[key].set("")

    def terminate(self, keypress_event=None):
        print("Terminating.")
        self.root.destroy()
