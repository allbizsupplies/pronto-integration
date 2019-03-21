
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json
import pyodbc
from urllib.parse import parse_qs, urlsplit
import yaml


class OrderRequestHandler(BaseHTTPRequestHandler):


    def do_GET(self):
        params = parse_qs(urlsplit(self.path).query)
        data = dict()

        if 'order' in params.keys():
            try:
                oid = int(params['order'][0])

                # Get the order
                oid = params['order'][0]
                (order, error) = client.get_order(oid)

                if error:
                    data['error'] = error

                # Write the response
                if order:
                    data['order'] = order
                else:
                    data['error'] = "Order " + str(oid) + " not found."
            except ValueError as ex:
                data['error'] = params['order'][0] + " is not a valid order number."
        else:
            data['error'] = "No order number given."
            
        body = json.dumps(data)
        # print(body)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body.encode("UTF-8"))


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
        

    def get_order(self, oid):
        order = None
        error = None

        cursor = self.conn.cursor()

        # Just get the entire job record.
        cursor.execute(
            'SELECT * FROM Allbiz WHERE "jobsheet number" = ?',
            oid
        )
        
        # Get column names
        columns = [column[0] for column in cursor.description]

        # Get the first row
        row = cursor.fetchone()
        
        if row:
            record = dict(zip(columns, row))
            order = {
                'items': list()
            }

            # Get the items
            for field in self.fields['items']:
                item_code = record[field['code']]

                if item_code:
                    # Trim and convert to all caps.
                    item_code = item_code.strip().upper()

                    description = record[field['description']]
                    quantity = record[field['quantity']]
                    price = record[field['unit_price']]

                    # Prepend "ALL-" to code if in list
                    if item_code in item_codes:
                        item_code = "ALL-" + item_code

                    # Add the item to the order
                    order['items'].append({
                        'item_code': item_code,
                        'description': description,
                        'quantity': quantity,
                        'price': price,
                    })

            # Get the art
            art = 0.00
            for field in self.fields['art']:
                price = record[field['price']]

                if price:
                    price = float(price)
                    art = art + price

            if art > 0.00:
                order['items'].append({
                        'item_code': "ART",
                        'quantity': "1",
                        'price': str(art),
                    })
        else:
            error = "Order " + str(oid) + " not found."

        return (order, error)



# Get the FM settings
with open("settings.yml") as stream:
    settings = yaml.load(stream)

# Get the list of item codes
item_codes = [line.rstrip() for line in open('item_codes.txt')]

# Get the FileMaker client
client = FMClient(settings)

# Start the HTTP Srever
port = settings["fm_port"]
server_address = ('', port)
httpd = ThreadingHTTPServer(server_address, OrderRequestHandler)
print("Listening on port " + str(port))
httpd.serve_forever()


