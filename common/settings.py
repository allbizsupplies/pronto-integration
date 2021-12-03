
import os
import yaml

INVALID_ACCOUNT_CODES = [
    None,
    "ACCOUNT",
    "CASH",
    "POS DEPOSIT",
    "COD ACCOUNT",
]

VALID_ACCOUNT_CODE_PATTERN = "^(A|COD|P|K)[0-9]+$"


def get_settings(type):
    cwd = os.getcwd()
    settings_filepath = os.path.join(cwd, "settings.{}.yml".format(type))
    with open(settings_filepath) as file:
        return yaml.safe_load(file)
