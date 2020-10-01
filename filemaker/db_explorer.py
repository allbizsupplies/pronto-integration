
import json
import pyodbc
import sys
from urllib.parse import parse_qs, urlsplit
import yaml


class FMClient:

    def __init__(self, settings):
        self.dsn = settings["fm_dsn"]
        self.user = settings["fm_user"]
        self.password = settings["fm_password"]
        self.table = settings["fm_table"]
        self.fields = settings['fields']

        self.conn = self.get_connection()

    def get_connection(self):
        conn = pyodbc.connect(
            DSN=self.dsn,
            UID=self.user,
            PWD=self.password,
            encoding="utf-8")

        conn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
        conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
        conn.setencoding("utf-8")

        return conn

    def fetch(self, order_id):
        cursor = self.conn.cursor()

        # Just get the entire job record.
        columns = ",".join(['"{}"'.format(column) for column in COLUMNS])
        statement = 'SELECT {} FROM Allbiz WHERE "jobsheet number" = ?'.format(
            columns)
        cursor.execute(statement, order_id)

        # Get column names
        columns = [column[0] for column in cursor.description]

        # Get the first row
        row = cursor.fetchone()
        if row:
            record = dict(zip(columns, row))
            job_name = record["Job Name"]
            print(job_name)


# Get the FM settings
with open("../settings.filemaker.yml") as stream:
    settings = yaml.load(stream)

# Get the FileMaker client
client = FMClient(settings)
client.fetch(sys.argv[1])
