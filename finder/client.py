
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
        columns.append(fields["contact"])
        self.columns = ",".join([f'"{column}"' for column in columns])

    def get_connection(self):
        conn = pyodbc.connect(
            DSN=self.dsn,
            UID=self.user,
            PWD=self.password,
            encoding="utf-8")
        return conn

    def fetch_records(self, id=None, search_terms=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        id_field = self.fields['id']

        def row_to_record(row):
            columns = [column[0] for column in cursor.description]
            record = dict(zip(columns, row))
            return record

        records = {}
        if id:
            statement = (f'SELECT {self.columns}'
                         f' FROM {self.table}'
                         f' WHERE "{self.fields["id"]}" = ?')
            cursor.execute(statement, id)
            row = cursor.fetchone()
            if row:
                record = row_to_record(row)
                id = int(record[id_field])
                records[id] = record
        elif search_terms:
            statement = f'SELECT {self.columns} FROM {self.table} WHERE '
            for index, search_term in enumerate(search_terms):
                if index > 0:
                    statement += " AND "
                job_name_condition = ("("
                                      f'LOWER("{self.fields["job_name"]}")'
                                      f" LIKE LOWER('%{search_term}%')"
                                      ")")
                contact_condition = ("("
                                     f'LOWER("{self.fields["contact"]}")'
                                     f" LIKE LOWER('%{search_term}%')"
                                     ")")
                statement += (f"({job_name_condition} OR {contact_condition})")
            print(statement)
            cursor.execute(statement)
            rows = cursor.fetchall()
            for row in rows:
                record = row_to_record(row)
                id = int(record[id_field])
                if id not in records:
                    records[id] = record
        return records

    def find_orders(self, query):

        # If the query is a number, find records where order ID matches the
        # query. Perform all other searches on the job name and contact name.
        records = {}
        if query.isdigit():
            records = self.fetch_records(id=int(query))
        else:
            search_terms = filter(lambda s: s != "", query.split(" "))
            records = self.fetch_records(search_terms=search_terms)

        orders = []
        for id, record in records.items():

            # Get the job name.
            job_name = record[self.fields['job_name']]

            # Get the customer's reference number.
            reference = record[self.fields['ref']]

            # Get the first phone number.
            phone_number = record[self.fields['phone_number']]
            if phone_number:
                phone_number = phone_number.split("/")[0].strip()
            order = {
                'id': id,
                'job_name': job_name,
                'phone_number': phone_number,
                'reference': reference,
                'items': list()
            }

            # Add the account code if it is valid.
            account_code = record[self.fields['account_code']]
            if is_valid_account_code(account_code):
                order['account_code'] = account_code

            orders.append(order)
        return orders


def is_valid_account_code(account_code):
    if account_code in INVALID_ACCOUNT_CODES:
        return False
    matches = re.match(VALID_ACCOUNT_CODE_PATTERN, account_code)
    return matches is not None
