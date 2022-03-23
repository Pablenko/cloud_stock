import json
import os
from pathlib import Path


STOCK_CONFIGURATION_FILE = "stock_config.json"
MANAGEMENT_TOPICS = {"transactions_completed_topic": "completed"}


def load_configuration():
    this_file_dir = os.path.dirname(os.path.realpath(__file__))
    with open(Path(this_file_dir) / STOCK_CONFIGURATION_FILE, "r") as config_handle:
        config = json.load(config_handle)
        return config
