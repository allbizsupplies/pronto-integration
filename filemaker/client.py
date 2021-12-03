
import os
import pyodbc
import re

from common.settings import INVALID_ACCOUNT_CODES, VALID_ACCOUNT_CODE_PATTERN
from common.exceptions import OrderNotFoundException


class ODBCClient:

    def __init__(self, settings):
        self.dsn = settings["dsn"]
        self.user = settings["user"]
        self.password = settings["password"]
        self.table = settings["table"]
        fields = settings['fields']
        self.fields = fields
        # Collect the required columns.
        columns = []
        columns.append(fields["id"])
        columns.append(fields["ref"])
        columns.append(fields["job_name"])
        columns.append(fields["phone_number"])
        columns.append(fields["account_code"])
        for item_fields in fields["items"]:
            columns.append(item_fields["code"])
            columns.append(item_fields["description"])
            columns.append(item_fields["quantity"])
            columns.append(item_fields["unit_price"])
        for art_fields in fields["art"]:
            columns.append(art_fields["description"])
            columns.append(art_fields["quantity"])
            columns.append(art_fields["price"])
        for payment_fields in fields["payments"]:
            columns.append(payment_fields["amount"])
            columns.append(payment_fields["invoice"])
        self.columns = ",".join(['"{}"'.format(column) for column in columns])
        # Get the list of item codes.
        item_code_filepath = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "item_codes.txt")
        self.item_codes = [line.rstrip() for line in open(item_code_filepath)]

    def get_connection(self):
        conn = pyodbc.connect(
            DSN=self.dsn,
            UID=self.user,
            PWD=self.password,
            encoding="utf-8")
        return conn

    def fetch_record(self, oid):
        conn = self.get_connection()
        cursor = conn.cursor()
        statement = 'SELECT {columns} FROM {table} WHERE "jobsheet number" = ?'.format(
            columns=self.columns,
            table=self.table)
        cursor.execute(statement, oid)
        row = cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            record = dict(zip(columns, row))
            return record
        raise OrderNotFoundException(oid)

    def get_order(self, oid):
        order = None
        error = None
        record = self.fetch_record(oid)
        # Column names.
        reference = record[self.fields['ref']]
        if reference is None:
            reference = str(oid)
        # Get the part of the job name that comes before the separator
        # as this is usually the person or company's name.
        full_job_name = record[self.fields['job_name']]
        job_name = None
        if full_job_name:
            job_name = full_job_name.split(" - ")[0].strip()
        # Get the first phone number.
        full_phone_number = record[self.fields['phone_number']]
        phone_number = None
        if full_phone_number:
            phone_number = full_phone_number.split("/")[0].strip()
        order = {
            'job_name': job_name,
            'phone_number': phone_number,
            'reference': reference,
            'items': list()
        }
        # Add the account code if it is valid.
        account_code = record[self.fields['account_code']]
        if is_valid_account_code(account_code):
            order['account_code'] = account_code
        # Get the items.
        for field in self.fields['items']:
            item_code = record[field['code']]
            if item_code:
                # Trim and convert to all caps.
                item_code = item_code.strip().upper()
                description = record[field['description']]
                quantity = record[field['quantity']]
                price = record[field['unit_price']]
                if quantity is None:
                    error = "Order {} has a line ({}) with no quantity.".format(
                        str(oid), item_code)
                # Prepend "ALL-" to code if in list.
                if item_code in self.item_codes:
                    item_code = "ALL-" + item_code
                # Add the item to the order.
                order['items'].append({
                    'item_code': item_code,
                    'description': description,
                    'quantity': quantity,
                    'price': price,
                })
        # Get the art.
        art = 0.00
        for field in self.fields['art']:
            price = record[field['price']]
            if price:
                price = float(price)
                art = art + price
        if art > 0.00:
            order['items'].append({
                'item_code': "ALL-ART",
                'quantity': "1",
                'price': str(art),
            })
        # Get the payments.
        for field in self.fields['payments']:
            amount = record[field['amount']]
            if amount:
                price = float(amount)
                item = {
                    'item_code': "ALL-DEPPRINT",
                    'quantity': "-1",
                    'price': str(price),
                }
                invoice = record[field['invoice']]
                if invoice:
                    item['description'] = "Paid on invoice " + \
                        str(int(invoice))
                order['items'].append(item)
        return order


def is_valid_account_code(account_code):
    if account_code in INVALID_ACCOUNT_CODES:
        return False
    matches = re.match(VALID_ACCOUNT_CODE_PATTERN, account_code)
    return matches is not None
