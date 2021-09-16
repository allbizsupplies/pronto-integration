
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import traceback
from urllib.parse import parse_qs, urlsplit
import yaml

from server.editandprint.webclient import WebClient, OrderException
from server.common import get_settings


def start():
    """Start the HTTP server."""
    global client
    global settings
    settings = get_settings("editandprint")
    client = get_client({
        "username": settings["username"],
        "password": settings["password"]
    })
    port = settings["port"]
    server_address = ('', port)
    httpd = HTTPServer(server_address, OrderRequestHandler)
    print("Listening on port " + str(port))
    httpd.serve_forever()


def get_client(auth):
    "Get the ENP client."
    client = WebClient(auth)
    client.refresh_session()
    return client


class OrderRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Get the request parameters
        params = parse_qs(urlsplit(self.path).query)
        # Build the response data.
        data = dict()
        if 'order' in params.keys():
            try:
                oid = int(params['order'][0])
                # Get the order
                try:
                    oid = params['order'][0]
                    order = client.get_order(oid)
                    data['order'] = order.get_pronto_format()
                except OrderException as ex:
                    error = str(ex)
                    print("Error: {}".format(error))
                    data['error'] = error
                except Exception as ex:
                    print(traceback.format_exc())
                    error = "Oops, the program has run into a problem."
                    data['error'] = error
            except ValueError:
                data['error'] = params['order'][0] + \
                    " is not a valid order number."
        else:
            data['error'] = "No order number given."
        body = json.dumps(data)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body.encode("UTF-8"))
