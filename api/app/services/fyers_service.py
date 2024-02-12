from datetime import datetime
import logging
from app.services.rules_evaluation_service import EvaluationService
from app.services.telegram_service import telegram_send_message
from app.utils.validation import escape_telegram_reserved_chars
from app.config import CLIENT_ID
from app.services.fyers_auth_service import generate_access_token
from fyers_apiv3 import fyersModel
from app.utils.exchange_util import (
    indices_symbols,
    fyers_index_symbols,
    indices_trader_exchange,
    indices_lot_quantity,
    last_week_of_month,
)

access_token = generate_access_token()

if access_token != None:
    fyers = fyersModel.FyersModel(
        client_id=CLIENT_ID, is_async=False, token=access_token
    )
else:
    print("Fyers Login failed.")

# Setup one time data
today = datetime.today()
current_day = today.strftime("%A").upper()
symbol = indices_symbols.get(current_day)
index_symbol = fyers_index_symbols.get(current_day)
exchange = indices_trader_exchange.get(symbol)


def get_index_symbol_current_ltp():
    fyers_index_symbol = f"{exchange}:{index_symbol}-INDEX"
    try:
        if fyers:
            data = {"symbols": fyers_index_symbol}
            response = fyers.quotes(data=data)
            if response.get("code") == 200:
                lp_value = response["d"][0]["v"]["lp"]
                return lp_value
            else:
                error_message = response.get("message")
                return (
                    {"error": error_message}
                    if error_message
                    else {"error": "An unexpected error occurred."}
                )
    except Exception as e:
        return f"Error: {str(e)}"


def find_25_values_less_than_nearest_hundred(nearest_hundred):
    if index_symbol.lower() in ["niftybank", "sensex"]:
        values_less_than_nearest_hundred = [
            nearest_hundred - 100 * i for i in range(1, 26)
        ]
    elif index_symbol.lower() in ["nifty50", "finnifty"]:
        values_less_than_nearest_hundred = [
            nearest_hundred - 50 * i for i in range(1, 26)
        ]
    else:
        values_less_than_nearest_hundred = [
            nearest_hundred - 25 * i for i in range(1, 26)
        ]

    return values_less_than_nearest_hundred


def find_24_values_more_than_nearest_hundred(nearest_hundred):
    if index_symbol.lower() in ["niftybank", "sensex"]:
        values_more_than_nearest_hundred = [
            nearest_hundred + 100 * i for i in range(1, 25)
        ]
    elif index_symbol.lower() in ["nifty50", "finnifty"]:
        values_more_than_nearest_hundred = [
            nearest_hundred + 50 * i for i in range(1, 25)
        ]
    else:
        values_more_than_nearest_hundred = [
            nearest_hundred + 25 * i for i in range(1, 25)
        ]

    return values_more_than_nearest_hundred


def find_nearest_value(max_pain):
    if index_symbol.lower() in ["niftybank", "sensex"]:
        return round(max_pain / 100) * 100
    elif index_symbol.lower() in ["nifty50", "finnifty"]:
        return round(max_pain / 50) * 50
    else:
        return round(max_pain / 25) * 25


def get_list_of_nearest_50_symbol():
    try:
        max_pain = (
            get_index_symbol_current_ltp()
        )  # Assuming this function retrieves max_pain

        # Check if max_pain is numeric before further calculations
        if isinstance(max_pain, (int, float)):
            nearest_lp_round_value = find_nearest_value(max_pain)
            less_than_values = find_25_values_less_than_nearest_hundred(
                nearest_lp_round_value
            )
            more_than_values = find_24_values_more_than_nearest_hundred(
                nearest_lp_round_value
            )
            strike_price_values = (
                less_than_values + [nearest_lp_round_value] + more_than_values
            )
            strike_price_values_sorted = sorted(strike_price_values)
            return strike_price_values_sorted
        else:
            return (
                f"Error: {max_pain} is not a numeric value"
                if max_pain
                else "Error: Max pain retrieval failed."
            )
    except Exception as e:
        return f"Error: {e}"


def convert_symbol_in_expected_form(is_last_week_of_month, strikePrice, optionType):
    formatted_symbol = f"{exchange}:{symbol.upper()}"
    current_date = datetime.now()
    year = current_date.year % 100
    month = current_date.strftime("%b")[:3].upper()
    day = current_date.day

    weekly_expiray_month_dict = {
        "JAN": "1",
        "FEB": "2",
        "MAR": "3",
        "APR": "4",
        "MAY": "5",
        "JUN": "6",
        "JUL": "7",
        "AUG": "8",
        "SEP": "9",
        "OCT": "O",
        "NOV": "N",
        "DEC": "D",
    }

    # Format the symbol based on the expiry type (weekly or monthly)
    if is_last_week_of_month == False:
        month_abbr = weekly_expiray_month_dict[month]
        formatted_symbol += f"{year:02d}{month_abbr}{day:02d}{strikePrice}{optionType}"
    elif is_last_week_of_month == True:
        formatted_symbol += f"{year:02d}{month}{strikePrice}{optionType}"
    else:
        raise ValueError("Invalid expiry_type. Use 'weekly' or 'monthly'.")

    return formatted_symbol


def fyers_option_chain(option_type):
    today = datetime.today()
    year = today.year
    month = today.month
    day = today.day
    formatted_symbols = []  # Initialize an empty list to store formatted symbols
    strikes = get_list_of_nearest_50_symbol()
    is_last_week_of_month = last_week_of_month(year, month, day)
    # Print the formatted strikes
    for index, formatted_strike in enumerate(strikes, start=1):
        formatted_symbol = convert_symbol_in_expected_form(
            is_last_week_of_month, formatted_strike, option_type
        )
        formatted_symbols.append(formatted_symbol)
    return formatted_symbols


def extract_shortname_lp_values(data):
    response = fyers.quotes(data=data)
    if response.get("code") == 200:
        result = response.get("d", [])
        # Extracting 'short_name' and 'lp' values and creating a new dictionary
        new_dict = {}
        for item in result:
            short_name = item.get("v", {}).get("short_name")
            lp = item.get("v", {}).get("lp")
            if short_name and lp is not None:
                new_dict[short_name] = {"ltp": lp}
        return new_dict
    else:
        error_message = response.get("message")
        return (
            {"error": error_message}
            if error_message
            else {"error": "An unexpected error occurred."}
        )


def fyers_get_strike_price_ltp(option_type):
    if option_type == "CE":
        ce_formatted_symbols_list = fyers_option_chain(option_type)
        ce_final_output = ",".join(ce_formatted_symbols_list)
        ce_data = {"symbols": ce_final_output}
        return extract_shortname_lp_values(ce_data)
    elif option_type == "PE":
        pe_formatted_symbols_list = fyers_option_chain(option_type)
        pe_final_output = ",".join(pe_formatted_symbols_list)
        pe_data = {"symbols": pe_final_output}
        return extract_shortname_lp_values(pe_data)


def get_fyers_quote():
    ce_option_chain = fyers_get_strike_price_ltp("CE")
    pe_option_chain = fyers_get_strike_price_ltp("PE")

    return ce_option_chain, pe_option_chain, symbol


def send_telegram_message(message):
    escaped_message = escape_telegram_reserved_chars(message)
    telegram_send_message(EvaluationService.chat_ids, escaped_message)


def place_fyers_order(trade_symbol, isExit):
    try:
        if isExit is True:
            if buy_option(trade_symbol, 1) == True:
                print("Order Exit Success!")
                return True
        else:
            if sell_option(trade_symbol, 1) == True:
                print("Sell Order Success!")
                return True
    except Exception as e:
        logging.info("Exception placing order: {e}")
        return False


def buy_option(trading_symbol, quantity):
    formatted_symbol = f"{exchange}:{trading_symbol}"
    # Place an order
    try:
        data = {
            "symbol": formatted_symbol,
            "qty": indices_lot_quantity.get(symbol) * quantity,
            "type": 2,
            "side": 1,
            "productType": "INTRADAY",
            "limitPrice": 0,
            "stopPrice": 0,
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": False,
            "orderTag": "tag1",
        }
        response = fyers.place_order(data=data)
        print(response)
        order_id = "Buy"
        send_telegram_message(
            "Position exited for " + trading_symbol + ". ID is: {}".format(order_id)
        )
        return True
    except Exception as e:
        send_telegram_message("Position exit failed for " + trading_symbol + ".")
        logging.info(
            "Position exit failed for " + trading_symbol + ": {}".format(e.message)
        )
        return False


def sell_option(trading_symbol, quantity):
    formatted_symbol = f"{exchange}:{trading_symbol}"
    try:
        data = {
            "symbol": formatted_symbol,
            "qty": indices_lot_quantity.get(symbol) * quantity,
            "type": 2,
            "side": -1,
            "productType": "INTRADAY",
            "limitPrice": 0,
            "stopPrice": 0,
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": False,
            "orderTag": "tag1",
        }
        response = fyers.place_order(data=data)
        print(response)
        order_id = "Sell"
        send_telegram_message(
            "Sell Order placed for " + trading_symbol + ". ID is: {}".format(order_id)
        )
        return True
    except Exception as e:
        send_telegram_message("Sell Order placement failed for " + trading_symbol + ".")
        logging.info(
            "Sell Order placement failed for "
            + trading_symbol
            + ": {}".format(e.message)
        )
        return False
