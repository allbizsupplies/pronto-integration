
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs, urlsplit
import yaml
from editandprint.webclient import WebClient, OrderException


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
                    data['error'] = str(ex)

            except ValueError:
                data['error'] = params['order'][0] + \
                    " is not a valid order number."
        else:
            data['error'] = "No order number given."

        body = json.dumps(data)
        # print(body)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body.encode("UTF-8"))


def get_client(auth):
    "Get the ENP client."

    client = WebClient(auth)
    client.refresh_session()

    return client


def get_settings():
    "Load settings from YAML file."

    with open("settings.editandprint.yml") as stream:
        return yaml.safe_load(stream)


def start(settings):
    "Start the HTTP server."
    settings = get_settings()

    port = settings["port"]
    server_address = ('', port)
    httpd = HTTPServer(server_address, OrderRequestHandler)
    print("Listening on port " + str(port))
    httpd.serve_forever()


if __name__ == "__main__":
    "Start the HTTP server."
    settings = get_settings()
    client = get_client({
        "username": settings["username"],
        "password": settings["password"]
    })
    start(settings)
