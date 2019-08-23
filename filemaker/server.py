
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import pyodbc
from urllib.parse import parse_qs, urlsplit
import yaml


class OrderRequestHandler(BaseHTTPRequestHandler):


    def do_GET(self):
        params = parse_qs(urlsplit(self.path).query)
        data = dict()

        if 'order' in params.keys():
            oid = None
            
            try:
                oid = int(params['order'][0])
            except ValueError as ex:
                print(ex)
                data['error'] = params['order'][0] + " is not a valid order number."

            # Get the order
            try:
                if oid is not None:
                    (order, error) = client.get_order(oid)

                    if error:
                        data['error'] = error

                    # Write the response
                    if order:
                        data['order'] = order
                    else:
                        data['error'] = "Order " + str(oid) + " not found."
            except Exception as ex:
                print("Error:", ex)
                data['error'] = "Oops, the program has run into a problem."                
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
                'reference': record[self.fields['ref']],
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

                    if quantity is None:
                        error = "Order {} has a line ({}) with no quantity.".format(str(oid), item_code)

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
                        'item_code': "ALL-ART",
                        'quantity': "1",
                        'price': str(art),
                    })

            # Get the payments
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
                        item['description'] = "Paid on invoice " + str(int(invoice))

                    order['items'].append(item)
        else:
            error = "Order " + str(oid) + " not found."

        return (order, error)



# Get the FM settings
with open("settings.filemaker.yml") as stream:
    settings = yaml.load(stream)

# Get the list of item codes
item_code_filepath = "filemaker/item_codes.txt"
item_codes = [line.rstrip() for line in open(item_code_filepath)]

# Get the FileMaker client
client = FMClient(settings)

# Start the HTTP Server
port = settings["fm_port"]
server_address = ('', port)
httpd = HTTPServer(server_address, OrderRequestHandler)
print("Listening on port " + str(port))
httpd.serve_forever()
