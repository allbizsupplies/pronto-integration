
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import pyodbc
from time import sleep
from urllib.parse import parse_qs, urlsplit
import yaml

from server.common import get_settings
from server.filemaker.client import FMClient


def start():
    """Start the HTTP Server."""
    global client
    global settings
    settings = get_settings("filemaker")
    # Get the FileMaker client.
    attempts = 0
    connected = False
    max_conn_attempts = int(settings["max_connection_attempts"])
    conn_attempt_delay = int(settings["connection_attempt_delay"])
    while (not connected):
        try:
            client = FMClient(settings)
            connected = True
            print("Connected to FileMaker via ODBC bridge.")
        except pyodbc.InterfaceError:
            attempts += 1
            if attempts < max_conn_attempts:
                print("Unable to connect to FileMaker. Retrying in {} seconds.".format(
                    conn_attempt_delay))
                sleep(conn_attempt_delay)
            else:
                print("Unable to connect to FileMaker. Shutting down.")
                quit()
    # Start the server.
    port = settings["port"]
    server_address = ('', port)
    httpd = HTTPServer(server_address, OrderRequestHandler)
    print("Listening on port " + str(port))
    httpd.serve_forever()


class OrderRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        data = dict()
        params = parse_qs(urlsplit(self.path).query)
        if 'order' in params.keys():
            # Get the order number.
            oid = None
            try:
                oid = int(params['order'][0])
            except ValueError:
                error = "{} is not a valid order number.".format(
                    params['order'][0])
                print("Error: {}".format(error))
                data['error'] = error
            # Get the order.
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
                print(ex)
                error = "Oops, the program has run into a problem."
                data['error'] = "Oops, the program has run into a problem."
        else:
            data['error'] = "No order number given."
        # Send the HTTP response.
        body = json.dumps(data)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body.encode("UTF-8"))
