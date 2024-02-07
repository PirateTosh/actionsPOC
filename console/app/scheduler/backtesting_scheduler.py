import os
import time
import psycopg2
import requests
import configparser
from datetime import datetime, timedelta


DATABASE_URL = "host=localhost port=5432 dbname=postgres user=postgres password=xorSprinters@8 sslmode=prefer connect_timeout=10"


def get_record_count_for_date(date_pattern):
    try:
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # SQL query to get the count for the given date pattern
        query = """
            SELECT COUNT(*) as record_count
            FROM opstra_data_v2
            WHERE datetime LIKE %s
        """

        # Execute the query with the date pattern as a parameter
        cursor.execute(query, (f"{date_pattern}%",))

        # Fetch the result
        result = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Return the record count
        return result[0] if result else 0

    except Exception as e:
        print(f"An error occurred: {e}")
        return 0


def job(api_baseurl, entry_price, threshold, guid, usertype, dates):
    try:
        headers = {"Content-Type": "application/json"}

        for date in dates:
            if date == dates[-1]:
                isLastDate = True
            else:
                isLastDate = False
            print(f"-----------Scheduler running for {date}")

            # Set the start and end time for the current date
            start_time = datetime.strptime(date + " 09:16", "%d%b%Y %H:%M")
            end_time = datetime.strptime(date + " 15:17", "%d%b%Y %H:%M")

            # Iterate over each minute within the specified range
            current_time = start_time
            while current_time <= end_time:
                print(f"Running for time: {current_time.strftime('%d%b%Y%H:%M')}")

                # Prepare the data with the current datetime value
                data = {
                    "entry_price": entry_price,
                    "threshold": threshold,
                    "guid": guid,
                    "usertype": usertype,
                    "date": current_time.strftime(
                        "%d%b%Y%H:%M"
                    ),  # Convert datetime to the required format
                    "isLastDate": isLastDate,
                }

                # Make the API request
                response = requests.post(
                    api_baseurl + "omegaTron_strategy", json=data, headers=headers
                )
                if response.text == "Data not found for date":
                    print("Data not found for this date")
                    break
                # Increment the current time by one minute
                current_time += timedelta(minutes=1)
                # time.sleep(2)

    except Exception as e:
        print(f"Error: {e}")


def get_config_parameters():
    # Get the current file's directory (assuming this script is inside the project)
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
        # usertype = config.get("configuration" "usertype")
    except ValueError:
        # Handle case where not a valid number
        print("Error fetching values from config, not a valid number")

    return api_baseurl, entry_price, threshold, guid


def run_omegaTron_backtesting():
    dates = [
        "5JAN2023",
        "12JAN2023",
        "19JAN2023",
        "26JAN2023",
        "2FEB2023",
        "9FEB2023",
        "16FEB2023",
        "23FEB2023",
        "2MAR2023",
        "9MAR2023",
        "16MAR2023",
        "23MAR2023",
        "29MAR2023",
        "6APR2023",
        "13APR2023",
        "20APR2023",
        "27APR2023",
        "4MAY2023",
        "11MAY2023",
        "18MAY2023",
        "25MAY2023",
        "1JUN2023",
        "8JUN2023",
        "15JUN2023",
        "22JUN2023",
        "28JUN2023",
        "6JUL2023",
        "13JUL2023",
        "20JUL2023",
        "27JUL2023",
        "3AUG2023",
        "10AUG2023",
        "17AUG2023",
        "24AUG2023",
        "31AUG2023",
        "7SEP2023",
        "14SEP2023",
        "21SEP2023",
        "28SEP2023",
        "5OCT2023",
        "12OCT2023",
        "19OCT2023",
        "26OCT2023",
        "2NOV2023",
        "9NOV2023",
        "16NOV2023",
        "23NOV2023",
        "30NOV2023",
        "7DEC2023",
        "14DEC2023",
        "21DEC2023",
        "28DEC2023",
    ]
    api_baseurl, entry_price, threshold, guid = get_config_parameters()
    job(api_baseurl, entry_price, threshold, guid, "Backtesting", dates)
