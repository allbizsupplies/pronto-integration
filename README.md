# Pronto POS Integrations

This repo contains clients for two integrations:

1. Fetch a job record from Allbiz's FileMaker Pro database and enter it into a Pronto sales order in Pronto Point of Sale.
2. Fetch a job record from Allbiz's EditAndPrint Web-to-Print website and enter it into a Pronto sales order in Pronto Point of Sale.

## How it works

1. A staff member has a print order that needs to be entered into Pronto Point of Sale to be invoiced.
2. They could key the order items manually, but that is slow and tedious, so...
3. They click on the taskbar shortcut to launch the "FM order"/"Web order" client, and key the order number.
4. The client fetches the order.
5. The client types the order items, payments and customer contact details into Pronto POS by simulating keyboard input.

## Installation

TODO

## Usage

1. Open a sale in Pronto POS.
2. Run the relevant client (either FileMaker or EditAndPrint)
3. Enter the order number.
4. Watch it key the order for you.
