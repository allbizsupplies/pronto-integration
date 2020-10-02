from bs4 import BeautifulSoup
from decimal import Decimal
from enum import Enum
import re

from editandprint.order import ShippingAddress, Order, Item, ItemOption


class ProductColumn(Enum):
    ID = 0
    IMAGE = 1
    DETAIL = 2
    QUANTITY = 4
    PRICE = 5


class ProductOptionColumn(Enum):
    DETAIL = 0
    QUANTITY = 1
    PRICE = 2


def build_response_data(order):
    data = {}

    # Build the address data.
    address = order["address"]
    data["delivery_address"] = {
        "name": address["company_name"],
        "address_1": address["street"],
        "address_2": address["suburb"],
        "address_3": address["state"],
        "address_4": "ATTN: " + address["contact_name"],
        "phone": address["contact_phone"],
        "postcode": address["postcode"],
    }

    # Build the items.
    data["items"] = []
    for item in order["items"]:
        description = item["label"]
        description += "\n" + "Quantity: " + item["quantity"]
        for option in item["options"]:
            description += "\n" + option["key"]
            if option["value"]:
                description += ": " + option["value"]
        data["items"].append({
            "item_code": item["item_code"],
            "description": description,
            "quantity": 1,
            "price": item["price"],
        })
    return data


def normalise_whitespace(string):
    # Remove leading and trailing whitespace
    string = string.strip()
    # Remove tab and newline characters
    string = string.replace("\n", " ").replace("\t", "")
    normalised_string = ""
    for component in string.split(" "):
        if component != "":
            if len(normalised_string) == 0:
                normalised_string = component
            else:
                normalised_string += " " + component
    return normalised_string


def parse_item(item_soup):
    item = Item()
    product_row_cells = item_soup["product_row"].find_all("td")
    product_detail_cell = product_row_cells[ProductColumn.DETAIL.value]
    # The product label is in span.text-primary,
    # but also includes newlines and tab characters that need to be removed.
    label_element = product_detail_cell.find("span", class_="text-primary")
    label = label_element.text.strip().replace(
        "\n", " ").replace("\t", "").replace("  ", "")
    item.label = label
    # The SKU is in the text in the detail cell, and is extracted with
    # with a regular expression.
    detail = product_detail_cell.text.strip().replace("\n", " ").replace("\t", "")
    sku_match = re.search(r"\( Product Sku : ([A-Za-z0-9:-]+) \)", detail)
    if sku_match:
        sku = sku_match.group(1)
        item_code = sku.split(":")[0]
        item.item_code = "ALL-" + item_code
    else:
        item.item_code = "ALL-MISC"
    # The Name is in the text in the detail cell, and is extracted with
    # with a regular expression.
    name_match = re.search(r"Name : (.+) \( Product Sku", detail)
    if name_match:
        name = name_match.group(1)
        item.name = name.strip()
    # The price is the text in the price cell, and has a dollar sign and
    # thousands separator that need to be removed.
    product_price_cell = product_row_cells[ProductColumn.PRICE.value]
    price = product_price_cell.text.replace("$", "").replace(",", "").strip()
    # Set the price to zero if the cell turns out to contain no price.
    item.price = Decimal(price) if price != "" else Decimal(0)
    # Ignore quantity
    item.quantity = 1
    for option_row in item_soup["product_option_rows"]:
        option = ItemOption()
        cells = option_row.find_all("td")
        option_detail_cell = cells[ProductOptionColumn.DETAIL.value]
        label = option_detail_cell.text.strip()
        if label == "":
            continue
        key, value = label.split(" : ")
        if value[:2] == "No":
            continue
        # Remove '(click "?" for x)' from option key.
        key = re.sub(r"\(click.+", "", key)
        option.key = key
        option.value = value
        option_price_cell = cells[ProductOptionColumn.PRICE.value]
        price = option_price_cell.text.replace(
            "$", "").replace(",", "").strip()
        if price:
            item.price += Decimal(price)
        item.options.append(option)
    return item


def parse_items(soup):
    wrapper = soup.find("div", class_="table-responsive ord_prd_list_table")
    table = wrapper.find("table", class_="dataTable")
    tbody = table.find("tbody")
    rows = tbody.find_all("tr", recursive=False)
    items = []
    item_soup = {}
    for tr in rows:
        if is_option_row(tr):
            item_soup["product_option_rows"].append(tr)
        else:
            # Parse the existing item and add it to the list of items.
            if "product_row" in item_soup.keys():
                item = parse_item(item_soup)
                items.append(item)
            item_soup = {
                "product_row": tr,
                "product_option_rows": []
            }
    # Parse the last item.
    if "product_row" in item_soup.keys():
        item = parse_item(item_soup)
        items.append(item)
    # Parse the shipping fee.
    shipping_item = parse_shipping_item(soup)
    if shipping_item:
        items.append(shipping_item)
    return items


def parse_shipping_item(soup):
    totals_wrapper = soup.find("div", class_="row ord_prd_list_table pt0")
    totals = totals_wrapper.find_all("h4")
    shipping_total = totals[1]
    price = shipping_total.find("span").text.replace(
        "$", "").replace(",", "").strip()
    if price == "0.00":
        return None
    shipping_item = Item(item_code="ALL-SHIPPING")
    shipping_item.price = Decimal(price)
    header_wrapper = soup.find("div", id="TabContent_orderdetail")
    table = header_wrapper.find("table", class_="table")
    tbody = table.find("tbody")
    columns = tbody.find_all("td")
    details = columns[3].find_all("dd")
    shipping_type = details[5].text
    shipping_item.label = shipping_type
    return shipping_item


def parse_order(html):
    soup = BeautifulSoup(html, "html.parser")
    shipping_address = parse_shipping_address(soup)
    items = parse_items(soup)
    order = Order(
        shipping_address=shipping_address,
        items=items
    )
    return order


def parse_shipping_address(soup):
    wrapper = soup.find("div", id="TabContent_orderdetail")
    table = wrapper.find("table", class_="table")
    tbody = table.find("tbody")
    columns = tbody.find_all("td")
    address = columns[1].find("address")
    # Get the address's lines.
    raw_address_html = normalise_whitespace(str(address))[9:-10]
    lines = raw_address_html.split("<br/>")
    # Discard the last line as it's always empty.
    lines.pop()
    address = {}
    # Extract contact name
    address["contact_name"] = BeautifulSoup(
        lines[0].strip(), "html.parser").text
    del lines[0]
    # Extract email, if present.
    if "@" in lines[0]:
        address["contact_email"] = lines[0].strip()
        del lines[0]
    # Extract company name.
    for index, line in enumerate(lines):
        soup = BeautifulSoup(line, "html.parser")
        if soup.text[:12] == "Company Name":
            address["company_name"] = soup.text.split(":")[1].strip()
            del lines[index]
            break
    # Extract phone number.
    for index, line in enumerate(lines):
        soup = BeautifulSoup(line, "html.parser")
        if soup.text[:12] == "Phone Number":
            address["contact_phone"] = soup.text.split(":")[1].strip()
            del lines[index]
            break
    # Extract postcode.
    for index, line in enumerate(lines):
        if re.match(r"^\d{4}$", line.strip()):
            address["postcode"] = line.strip()
            del lines[index]
            break
    # Extract country
    address["country"] = lines.pop().strip()
    # Merge and then split remaining lines into components
    components = " ".join(lines).split(", ")
    # Discard the last component if it's empty.
    if components[-1] == "":
        components.pop()
    # Extract the state and suburb.
    address["state"] = components.pop()
    address["suburb"] = components.pop()
    # Discard duplicate suburb.
    if len(components) > 1 and components[-1] == address["suburb"]:
        components.pop()
    # Use whatever's left as the street address
    address["street"] = " ".join(components)
    return ShippingAddress(**address)


def parse_payment(details):
    soup = details[3].find("dl")
    payment_details = soup.find_all("dd")
    method = payment_details[0].text.strip()
    payment = {
        "method": method,
        "date": payment_details[1].text.strip(),
        "transaction_id": payment_details[2].text.strip(),
    }
    payment["paid_in_full"] = False
    if method == "ANZ eGate":
        payment["paid_in_full"] = True
    return payment


def is_option_row(tr):
    return "class" in tr.attrs.keys() and "ord_prd_options" in tr.attrs["class"]
