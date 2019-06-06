
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import pyodbc
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
                data['error'] = params['order'][0] + " is not a valid order number."
        else:
            data['error'] = "No order number given."
            
        body = json.dumps(data)
        # print(body)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body.encode("UTF-8"))



def get_auth():
    "Get the auth secret from the user."

    print("Enter your admin login details for the Edit and Print site:")

    auth = { 
        "username": None,
        "password": None
    }

    while(auth["username"] is None):
        username = input("username: ")
        if username != "":
            auth["username"] = username

    while(auth["password"] is None):
        password = input("password: ")
        if password != "":
            auth["password"] = password

    return auth



def get_client(auth):
    "Get the ENP client."

    client = WebClient(auth)
    client.refresh_session()

    return client



def get_settings():
    "Load settings from YAML file."

    with open("settings.editandprint.yml") as stream:
        return yaml.load(stream)



def start():
    "Start the HTTP server."
    settings = get_settings()

    port = settings["port"]
    server_address = ('', port)
    httpd = HTTPServer(server_address, OrderRequestHandler)
    print("Listening on port " + str(port))
    httpd.serve_forever()



if __name__ == "__main__":
    auth = get_auth()
    client = get_client(auth)
    start()
    