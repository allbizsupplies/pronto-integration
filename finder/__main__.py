
import json
import subprocess

from common.exceptions import SaleNotOpenException, SubmitError
from common.pronto.controller import ThinClientController
from common.settings import get_settings
from finder.client import ODBCClient
from finder.gui import Gui


def main():
    gui = Gui("FileMaker Order Finder", on_submit)
    gui.show()


def on_submit(values):
    data = json.dumps({
        "query": values["query"]
    })
    completed_process = subprocess.run(
        ["pythonw", "-m", "finder.query", data], capture_output=True)
    output = completed_process.stdout.decode("utf-8").strip()
    data = json.loads(output)
    return data


if __name__ == "__main__":
    main()
