
import os
import pyodbc
import re

from common.settings import INVALID_ACCOUNT_CODES, VALID_ACCOUNT_CODE_PATTERN
from common.exceptions import OrderNotFoundException


class ODBCClient:

    def __init__(self, settings):
        self.connection = None
        self.dsn = settings["dsn"]
        self.user = settings["user"]
        self.password = settings["password"]
        self.table = settings["table"]
        fields = settings["fields"]
        self.fields = fields
        # Collect the required columns.
        columns = []
        columns.append(fields["id"])
        columns.append(fields["ref"])
        columns.append(fields["job_name"])
        columns.append(fields["phone_number"])
        columns.append(fields["account_code"])
        columns.append(fields["contact"])
        columns.append(fields["created_at"])
        columns.append(fields["due_date"])
        columns.append(fields["job_type"])
        columns.append(fields["status"])
        columns.append(fields["location"])
        self.columns = ",".join([f'"{column}"' for column in columns])

    def get_connection(self):
        if not self.connection:
            self.connection = pyodbc.connect(
                DSN=self.dsn,
                UID=self.user,
                PWD=self.password,
                encoding="utf-8",
                autocommit=True)
        return self.connection

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def fetch_record(self, id):
        id = int(id)
        records = self.fetch_records(id=id)
        if id in records:
            return records[id]
        return None

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
            statement += f'ORDER BY "{self.fields["created_at"]}" DESC'
            cursor.execute(statement)
            rows = cursor.fetchall()
            for row in rows:
                record = row_to_record(row)
                id = int(record[id_field])
                if id not in records:
                    records[id] = record

        return records

    def update_record(self, id, values):
        conn = self.get_connection()
        cursor = conn.cursor()
        id_field = self.fields['id']
        statement = f"UPDATE {self.table} SET"
        for field_name, value in values.items():
            if isinstance(value, str):
                statement += f' "{self.fields[field_name]}" = \'{value}\''
            elif isinstance(value, int):
                statement += f' "{self.fields[field_name]}" = {value}'
        statement += f' WHERE "{self.fields["id"]}" = ?'
        cursor.execute(statement, id)
        return self.fetch_record(id)

    def find_orders(self, query):

        # If the query is a number, find records where order ID matches the
        # query. Perform all other searches on the job name and contact name.
        records = {}
        if query.isdigit():
            records = self.fetch_records(id=int(query))
        else:
            search_terms = filter(lambda s: s != "", query.split(" "))
            records = self.fetch_records(search_terms=search_terms)

        return [self.order_from_record(id, record)
                for id, record in records.items()]

    def update_order(self, order_id, values):
        record = self.update_record(order_id, values)
        return self.order_from_record(order_id, record)

    def order_from_record(self, id, record):
        created_at = record[self.fields['created_at']]
        due_date = record[self.fields['due_date']]
        if due_date:
            due_date = due_date.isoformat()
        return {
            "id": id,
            "job_name": record[self.fields['job_name']],
            "contact": record[self.fields['contact']],
            "reference": record[self.fields['ref']],
            "job_type": record[self.fields['job_type']],
            "status": record[self.fields['status']],
            "created_at": created_at.isoformat(timespec="seconds"),
            "due_date": due_date,
            "location": record[self.fields['location']],
        }


def is_valid_account_code(account_code):
    if account_code in INVALID_ACCOUNT_CODES:
        return False
    matches = re.match(VALID_ACCOUNT_CODE_PATTERN, account_code)
    return matches is not None
