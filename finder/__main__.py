
import json
import subprocess

from common.exceptions import SaleNotOpenException, SubmitError
from common.pronto.controller import ThinClientController
from common.settings import get_settings
from finder.client import ODBCClient
from finder.gui import Gui


LOCATION_COLLECTED = "COLLECTED"


def main():
    gui = Gui(
        "FileMaker Order Finder",
        on_submit_search,
        on_mark_order_collected)
    gui.show()


def on_submit_search(query):
    data = json.dumps({
        "query": query
    })
    completed_process = subprocess.run(
        ["pythonw", "-m", "finder.fetch", data], capture_output=True)
    output = completed_process.stdout.decode("utf-8").strip()
    data = json.loads(output)
    return data


def on_mark_order_collected(order_id):
    data = json.dumps({
        "id": order_id,
        "values": {
            "location": LOCATION_COLLECTED,
        }
    })
    completed_process = subprocess.run(
        ["pythonw", "-m", "finder.update", data], capture_output=True)
    output = completed_process.stdout.decode("utf-8").strip()
    data = json.loads(output)
    return data


if __name__ == "__main__":
    main()
