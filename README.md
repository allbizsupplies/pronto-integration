Pronto POS Integrations
=======================

This repo contains clients and servers for two integrations:

1. Fetch a job record from Allbiz's FileMaker Pro database and enter it into a Pronto sales order in Pronto Point of Sale.
2. Fetch a job record from Allbiz's EditAndPrint Web-to-Print website and enter it into a Pronto sales order in Pronto Point of Sale.

Both integrations consist of two parts:

1. An HTTP server intended to be accessible only on a local network.
2. An HTTP client and automation tool that needs to be executed on a computer with A sales order open in Pronto Point of Sale, in the Pronto Thin Client.

How it works
------------

### How the client works

1. A staff member has a print order that needs to be entered into Pronto Point of Sale to be invoiced.
2. They could key the order items manually, but that is slow and tedious, so...
3. They click on the taskbar shortcut to launch the "FM order"/"Web order" client, and key the order number.
4. The client requests the order from the server, which sends back the data as a JSON object.
5. The client types the order items, payments and customer contact details into Pronto POS by simulating keyboard input.

### How the FileMaker server works

1. The server receives an HTTP request from the client, with an order number.
2. The server connects to the Windows data source that provides access to FileMaker;s SQL database (ODBC bridge)
3. The server queries the SQL database for the order using its order number.
4. The server compiles a list of order lines, payments and the customer's contact details, and send this back to the client in JSON format.

### How the EditAndPrint server works

1. The server receives an HTTP request from the client, with an order number.
2. The server logs into the Web-to-print shop as an administrator, and requests the order view page.
3. The server parses the order page HTML and extracts the order details.
4. The server compiles a list of order lines, payments and the customer's contact details, and send this back to the client in JSON format.

Installation
------------

### Server

Requirements:
- Windows
- Python 3.8 or newer.

1. Download the project to the FileMaker server (or a connected network drive)
2. Copy `example.settings.editandprint.yml` and `example.settings.filemaker.yml` to `settings.editandprint.yml` and `settings.filemaker.yml`,respectively, and fill in the database and login details.
3. Start the servers by executing the batch files `settings.editandprint.yml` and `settings.filemaker.yml`.

Security considerations:
- Servers should listen on non-standard HTTP ports (e.g. 3300 and 3301).
- These ports should not be accessible from the Internet, only from LAN. These servers do not authenticate requests.

### Client

1. Put a shortcut on the desktop for each client's executable, and assign a keyboard shortcut to each. (e.g. Ctrl+Alt+F and Ctrl+Alt+W).
2. Make sure the POS computer is on the same LAN as the server.

Usage
-----

1. Open a sale in Pronto POS.
2. Run the relevant client (either FileMaker or EditAndPrint)
3. Enter the order number.
4. Watch it key the order for you.
