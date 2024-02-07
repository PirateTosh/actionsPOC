import os
import requests
import configparser
from datetime import datetime


def job(api_baseurl, entry_price, threshold, guid):
    try:
        data = {"entry_price": entry_price, "threshold": threshold, "guid": guid}
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            api_baseurl + "omegaTron_strategy", json=data, headers=headers
        )

        print(f"---------- OmegaTron Strategy Executed at {datetime.now().strftime('%m/%d/%Y %H:%M:%S')} ----------\n")
        print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def get_config_parameters():
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Construct the absolute path to your ini file
    config_path = os.path.join(current_dir, "config", "omegaTron_config.ini")

    # Read from the config file - omegaTron_config.ini
    config = configparser.ConfigParser()
    config.read(config_path)
    # Access configuration values
    try:
        api_baseurl = config.get("api_connection", "api_baseurl")
        entry_price = float(config.get("configuration", "entry_price"))
        threshold = float(config.get("configuration", "threshold"))
        guid = config.get("configuration", "guid")
    except ValueError:
        # Handle case where not a valid number
        print("Error fetching values from config, not a valid number")

    return api_baseurl, entry_price, threshold, guid


def run_omegaTron_strategy():
    api_baseurl, entry_price, threshold, guid = get_config_parameters()
    job(api_baseurl, entry_price, threshold, guid)
