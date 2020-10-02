
import os
import yaml


def get_settings(type):
    cwd = os.getcwd()
    settings_filepath = os.path.join(cwd, "settings.{}.yml".format(type))
    with open(settings_filepath) as file:
        return yaml.safe_load(file)
