
import json
import pyodbc
from urllib.parse import parse_qs, urlsplit
import yaml


TEST_ORDER_ID = 31912


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

    def show_table(self):
        cursor = self.conn.cursor()

        # Just get the entire job record.
        cursor.execute(
            'SELECT * FROM Allbiz WHERE "jobsheet number" = ?',
            TEST_ORDER_ID
        )
        
        # Get column names
        columns = [column[0] for column in cursor.description]

        # Get the first row
        row = cursor.fetchone()

        # Print the columns
        for column in columns:
            print(column)


# Get the FM settings
with open("../settings.filemaker.yml") as stream:
    settings = yaml.load(stream)

# Get the FileMaker client
client = FMClient(settings)
client.show_table()
