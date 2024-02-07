from email.mime.application import MIMEApplication
import os
import smtplib
import ssl
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import psycopg2
from psycopg2 import sql
from datetime import datetime
import pandas as pd
from app.config import DATABASE_URL


def get_gmail_service():
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_file_path = os.path.abspath("credentials.json")
            print("Using credentials file:", credentials_file_path)
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def mail_backtesting_report(recipient_email="srs.paritosh7@gmail.com"):
    # Email configuration
    sender_email = "paritosh.singh@xorlabs.com"  # Your Gmail address
    subject = "Backtesting Report"

    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject

    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Go up to the parent directory
    parent_dir = os.path.dirname(current_dir)

    # Construct the absolute path to your file
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(current_dir))),
        "backtesting_results.xlsx",
    )

    # Attach the Excel file to the email
    with open(file_path, "rb") as file:
        attachment = MIMEApplication(file.read(), _subtype="xlsx")
        attachment.add_header(
            "Content-Disposition", "attachment", filename=os.path.basename(file_path)
        )
        message.attach(attachment)

    creds = get_gmail_service()

    # Connect to the Gmail API
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.ehlo_or_helo_if_needed()
        server.login(sender_email, creds.token)

        # Send the email
        server.sendmail(sender_email, recipient_email, message.as_string())

    print("Backtesting report email sent successfully!")


def send_mail(
    email_sender="paritosh.singh@xorlabs.com",
    email_password="luwj wucw zdgm uzht",
    email_receiver="paritosh.singh@xorlabs.com",
    subject="test mail",
    body="test",
    file_path="backtesting_results_summry.xlsx",
):
    # Create a multipart message
    em = MIMEMultipart()
    em["From"] = email_sender
    em["To"] = email_receiver
    em["Subject"] = subject

    # Attach text body
    em.attach(MIMEText(body, "plain"))

    # Attach the file
    attachment = open(file_path, "rb")
    file_mime = MIMEBase("application", "octet-stream")
    file_mime.set_payload((attachment).read())
    encoders.encode_base64(file_mime)
    file_mime.add_header(
        "Content-Disposition", "attachment; filename= %s" % file_path.split("/")[-1]
    )

    em.attach(file_mime)

    # Add SSL (layer of security)
    context = ssl.create_default_context()

    # Log in and send the email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())


# Example usage
email_sender = "write-email-here"
email_password = "write-password-here"
email_receiver = "write-email-receiver-here"
subject = "Check out my new video!"
body = """
I've just published a new video on YouTube: https://youtu.be/2cZzP9DLlkg
"""
file_path = "path/to/your/file.txt"  # Replace with the actual path to your file


def backtesting_report(date):
    xls_file_path = "backtesting_results.xlsx"
    date_without_time = datetime.strptime(date, "%d%b%Y%H:%M").strftime("%d%b%Y")

    # Check if the file exists
    if os.path.exists(xls_file_path):
        # Load existing data from the file
        df_existing = pd.read_excel(xls_file_path)

        # Create a DataFrame for the current date
        df_new = pd.DataFrame({"Date": [date_without_time]})
        df_new["Total Number of Trades"] = calculate_total_trades(date)
        pl_metrics = calculate_pl_metrics(date)

        df_new["Total Profit Booked"] = pl_metrics["Total Profit Booked"]
        df_new["Total Loss Booked"] = pl_metrics["Total Loss Booked"]
        df_new["Net P/L Booked"] = pl_metrics["Net P/L Booked"]
        df_new["Total Capital"] = 0
        df_new["Hit-rate %"] = pl_metrics["Hit-rate"]
        df_new["MaxDrawDown"] = pl_metrics["Max Loss"]
        df_new["MaxDrawDownSymbol"] = pl_metrics["Max Loss Symbol"]
        # Append the new data to the existing DataFrame
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)

        # Write the combined DataFrame to the Excel file
        df_combined.to_excel(xls_file_path, index=False)
    else:
        # If the file doesn't exist, create a new DataFrame and write it to the file
        df = pd.DataFrame({"Date": [date]})
        df["Total Number of Trades"] = calculate_total_trades(date)
        pl_metrics = calculate_pl_metrics(date)
        df["Total Profit Booked"] = pl_metrics["Total Profit Booked"]
        df["Total Loss Booked"] = pl_metrics["Total Loss Booked"]
        df["Net P/L Booked"] = pl_metrics["Net P/L Booked"]
        df["Total Capital"] = 0
        df["Hit-rate %"] = pl_metrics["Hit-rate"]
        df["MaxDrawDown"] = pl_metrics["Max Loss"]
        df["MaxDrawDownSymbol"] = pl_metrics["Max Loss Symbol"]
        df.to_excel(xls_file_path, index=False)

    if date_without_time == "28DEC2023":
        update_and_generate_summary(xls_file_path)


def update_and_generate_summary(file_path):
    # Read the Excel file into a DataFrame
    df = pd.read_excel(file_path)

    # Calculate the summary row
    summary_row = pd.Series(
        {
            "Date": "Summary",
            "Total Number of Trades": df["Total Number of Trades"].sum(),
            "Total Profit Booked": df["Total Profit Booked"].sum(),
            "Total Loss Booked": df["Total Loss Booked"].sum(),
            "Net P/L Booked": df["Net P/L Booked"].sum(),
            "Total Capital": df["Total Capital"].sum(),
            "Hit-rate %": df["Hit-rate %"].mean(),
            "MaxDrawDown": df["MaxDrawDown"].max(),
            "MaxDrawDownSymbol": df.loc[
                df["MaxDrawDown"].idxmax(), "MaxDrawDownSymbol"
            ],
        }
    )

    # Append the summary row to the DataFrame
    df = pd.concat([df, summary_row.to_frame().T], ignore_index=True)

    # Write the updated DataFrame back to the Excel file
    df.to_excel(file_path, index=False)


def process_data(input_data):
    ce_option_chain = {}
    pe_option_chain = {}

    for entry in input_data:
        datetime_str, call_ltp, put_ltp, strikes = entry

        # Extract relevant components from datetime
        if len(datetime_str) < 14:
            datetime_str = "0" + datetime_str

        # Extract relevant components from datetime
        year = datetime_str[7:9]
        month_str = datetime_str[2:5]
        day = datetime_str[0:2]

        # Convert month abbreviation to numeric value
        month_dict = {
            "JAN": "01",
            "FEB": "02",
            "MAR": "03",
            "APR": "04",
            "MAY": "05",
            "JUN": "06",
            "JUL": "07",
            "AUG": "08",
            "SEP": "09",
            "OCT": "10",
            "NOV": "11",
            "DEC": "12",
        }
        month = month_dict.get(month_str.upper(), "00")

        # Create the key in the desired format for both CE and PE
        ce_key = f"NIFTY{year}{month}{day}{str(int(strikes))}CE"
        pe_key = f"NIFTY{year}{month}{day}{str(int(strikes))}PE"

        # Add the keys to the output dictionaries if not present
        if ce_key not in ce_option_chain:
            ce_option_chain[ce_key] = {"ltp": 0}
        if pe_key not in pe_option_chain:
            pe_option_chain[pe_key] = {"ltp": 0}

        # Set 'ltp' to the value of call_ltp or put_ltp if not None
        if call_ltp is not None:
            ce_option_chain[ce_key]["ltp"] = call_ltp
        if put_ltp is not None:
            pe_option_chain[pe_key]["ltp"] = put_ltp

    return ce_option_chain, pe_option_chain


def get_backtesting_quote(date):
    opstra_data = fetch_opstra_data(date)
    ce_option_chain, pe_option_chain = process_data(opstra_data)

    return ce_option_chain, pe_option_chain, "NIFTY"


def storeTransaction(user_id, transaction_type, stock_symbol, quantity, price, date):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(DATABASE_URL)

        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()

        if date is None:
            # Get the current timestamp
            timestamp = datetime.now()
        else:
            # timestamp = date
            timestamp = date
        # Define the SQL query to insert the transaction details into the 'transactions' table
        query = sql.SQL(
            """
            INSERT INTO transactions (user_id, transaction_type, stock_symbol, quantity, price, backtesting_date)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        )

        # Execute the query with the provided parameters
        cursor.execute(
            query, (user_id, transaction_type, stock_symbol, quantity, price, timestamp)
        )

        # Commit the transaction to persist the changes
        conn.commit()

    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def fetch_opstra_data(date_str):
    try:
        if date_str and date_str[0] == "0":
            date = date_str.lstrip("0").upper()
            # date = date.upper()
        else:
            date = date_str.upper()
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Parameterized query with the date filter
        query = """
            SELECT datetime, callltp, putltp, strikes
            FROM opstra_data_v2
            WHERE datetime LIKE %s
            ORDER BY datetime ASC 
        """

        # Using % for LIKE clause, and passing the date as a tuple
        cursor.execute(query, (f"{date}%",))
        # Fetch all rows
        rows = cursor.fetchall()

        # Return the fetched data
        return rows

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def calculate_total_trades(date):
    try:
        # Remove time from the date
        date_without_time = datetime.strptime(date, "%d%b%Y%H:%M").strftime("%d%b%Y")

        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Parameterized query with the date filter
        query = """
            SELECT COUNT(*)
            FROM transactions
            WHERE backtesting_date LIKE %s
        """

        # Using % for LIKE clause, and passing the date as a tuple
        cursor.execute(query, (f"{date_without_time}%",))
        # Fetch the count
        count = cursor.fetchone()[0]

        # Return the total trades count
        return count

    except Exception as e:
        print(f"Error fetching total trades: {e}")
        return None

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def calculate_pl_metrics(date):
    try:
        date_without_time = datetime.strptime(date, "%d%b%Y%H:%M").strftime("%d%b%Y")

        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Parameterized query with the date filter
        query = sql.SQL(
            """
            SELECT stock_symbol, transaction_type, price
            FROM transactions
            WHERE backtesting_date LIKE {}
        """
        ).format(sql.Literal(f"{date_without_time}%"))

        # Using % for LIKE clause, and passing the date as a tuple
        cursor.execute(query)
        # Fetch all rows
        rows = cursor.fetchall()

        sold_transactions = {}
        bought_transactions = {}
        profits = []
        losses = []

        for row in rows:
            stock_symbol, transaction_type, price = row
            if transaction_type == "sold":
                profits.append({"stock_symbol": stock_symbol, "price": price})
            elif transaction_type == "bought":
                losses.append({"stock_symbol": stock_symbol, "price": price})

        # Calculate hit rate
        total_trades = len(profits) + len(losses)
        hit_rate = (len(profits) / total_trades) * 100 if total_trades > 0 else 0

        # Calculate total profit, total loss, and net P/L
        total_profit = sum(entry["price"] for entry in profits)
        total_loss = sum(entry["price"] for entry in losses)
        net_pl = total_profit - total_loss

        # Find maximum loss
        max_loss_entry = max(losses, key=lambda entry: entry["price"], default=None)
        max_loss_symbol = max_loss_entry["stock_symbol"] if max_loss_entry else None
        max_loss = max_loss_entry["price"] if max_loss_entry else 0.0

        # Return the calculated metrics
        return {
            "Total Profit Booked": total_profit,
            "Total Loss Booked": total_loss,
            "Net P/L Booked": net_pl,
            "Profits": profits,
            "Losses": losses,
            "Max Loss Symbol": max_loss_symbol,
            "Max Loss": max_loss,
            "Hit-rate": hit_rate,
        }

    except Exception as e:
        print(f"Error calculating P/L metrics: {e}")
        return None

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# def calculate_pl_metrics(date):
#     try:
#         date_without_time = datetime.strptime(date, "%d%b%Y%H:%M").strftime("%d%b%Y")

#         conn = psycopg2.connect(DATABASE_URL)
#         cursor = conn.cursor()

#         # Parameterized query with the date filter
#         query = sql.SQL(
#             """
#             SELECT stock_symbol, transaction_type, price
#             FROM transactions
#             WHERE backtesting_date LIKE {}
#         """
#         ).format(sql.Literal(f"{date_without_time}%"))

#         # Using % for LIKE clause, and passing the date as a tuple
#         cursor.execute(query)
#         # Fetch all rows
#         rows = cursor.fetchall()

#         sold_transactions = {}
#         bought_transactions = {}
#         losses = {}

#         for row in rows:
#             stock_symbol, transaction_type, price = row
#             if transaction_type == "sold":
#                 sold_transactions[stock_symbol] = price
#             elif transaction_type == "bought":
#                 bought_transactions[stock_symbol] = price

#         profits = {}

#         # Calculate profits and losses
#         for stock_symbol, sold_price in sold_transactions.items():
#             if stock_symbol in bought_transactions:
#                 bought_price = bought_transactions[stock_symbol]
#                 if sold_price > bought_price:
#                     profits[stock_symbol] = sold_price - bought_price
#                 elif sold_price < bought_price:
#                     losses[stock_symbol] = bought_price - sold_price

#         total_profit = sum(profits.values())
#         total_loss = sum(losses.values())
#         net_pl = total_profit - total_loss

#         # Find maximum loss
#         max_loss_symbol = max(losses, key=losses.get, default=None)
#         max_loss = losses[max_loss_symbol] if max_loss_symbol else 0.0

#         # Return the calculated metrics
#         return {
#             "Total Profit Booked": total_profit,
#             "Total Loss Booked": total_loss,
#             "Net P/L Booked": net_pl,
#             "Profits": profits,
#             "Losses": losses,
#             "Max Loss Symbol": max_loss_symbol,
#             "Max Loss": max_loss,
#         }

#     except Exception as e:
#         print(f"Error calculating P/L metrics: {e}")
#         return None

#     finally:
#         # Close the cursor and connection
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()
