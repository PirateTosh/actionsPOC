import subprocess
import time
from datetime import datetime, timedelta
import os


def run_script():
    try:
        current_directory = os.getcwd()
        print(f"Current working directory: {current_directory}")
        subprocess.run(
            [
                "python",
                "\scripts\scrape_securityArchives_nse.py"
                # "D:\OmegaTronBranch0.2WorkingDir\scripts\scrape_securityArchives_nse.py",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running security archives script: {e}")

    try:
        subprocess.run(
            [
                "python",
                "D:\OmegaTronBranch0.2WorkingDir\scripts\scrape_securityArchives_nse.py",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running delta corp historical data script: {e}")


def run_daily_at_1245pm():
    while True:
        # Get current time
        now = datetime.now()

        # Calculate the time until 12:45 pm of the next day
        next_run_time = datetime(now.year, now.month, now.day, 18, 32, 40)
        if now >= next_run_time:
            next_run_time += timedelta(days=1)

        # Calculate the sleep duration
        sleep_duration = (next_run_time - now).total_seconds()

        print(f"Next run at {next_run_time}. Sleeping for {sleep_duration} seconds.")
        time.sleep(sleep_duration)

        # Run the script
        run_script()


if __name__ == "__main__":
    run_daily_at_1245pm()
