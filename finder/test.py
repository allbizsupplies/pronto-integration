

import json
import pyodbc
from finder.client import ODBCClient
from common.settings import get_settings
import subprocess

query = "31912"

completed_process = subprocess.run(
    ["python", "-m", "finder.query", query], capture_output=True)
output = completed_process.stdout.decode("utf-8").strip()
data = json.loads(output)
print(data["orders"])
