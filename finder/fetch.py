
import json
import pyodbc
import sys

from finder.client import ODBCClient
from common.settings import get_settings


def main():
    data = json.loads(sys.argv[1])
    settings = get_settings("filemaker")
    client = ODBCClient(settings)
    orders = client.find_orders(data["query"])
    print(json.dumps({
        "orders": orders,
    }))


if __name__ == "__main__":
    main()
