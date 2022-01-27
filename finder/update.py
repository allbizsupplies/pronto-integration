
import json
import pyodbc
import sys

from finder.client import ODBCClient
from common.settings import get_settings


def main():
    data = json.loads(sys.argv[1])
    settings = get_settings("filemaker")
    client = ODBCClient(settings)
    order = client.update_order(data["id"], data["values"])
    print(json.dumps({
        "order": order
    }))


if __name__ == "__main__":
    main()
