import logging
import platform
import shutil
from kiteconnect import KiteConnect
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
import time, pyotp
from app.services.rules_evaluation_service import EvaluationService
from app.services.telegram_service import telegram_send_message
from app.utils.validation import escape_telegram_reserved_chars
from app.utils.exchange_util import (
    indices_zerodha_exchange,
    indices_symbols,
    indices_lot_quantity,
)
from app.config import (
    ZERODHA_API_KEY,
    ZERODHA_API_SECRET,
    ZERODHA_USER_ID,
    ZERODHA_USER_PWD,
    ZERODHA_TOTP_KEY,
)
from datetime import datetime


def find_chrome_binary():
    # Search for the Chrome binary in common locations
    chrome_binary = shutil.which("google-chrome")

    if chrome_binary is None:
        raise Exception(
            "Chrome binary not found. Please specify the path manually or make sure Chrome is installed."
        )

    return chrome_binary


def login_in_zerodha():
    pass


def send_telegram_message(message):
    escaped_message = escape_telegram_reserved_chars(message)
    telegram_send_message(EvaluationService.chat_ids, escaped_message)


def place_zerodha_order(trade_symbol, isExit):
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
    # Place an order
    try:
        order_id = kite.place_order(
            tradingsymbol=trading_symbol,
            exchange=indices_zerodha_exchange.get(symbol),
            transaction_type=kite.TRANSACTION_TYPE_BUY,
            quantity=indices_lot_quantity.get(symbol) * quantity,
            variety=kite.VARIETY_REGULAR,
            order_type=kite.ORDER_TYPE_MARKET,
            product=kite.PRODUCT_NRML,
            validity=kite.VALIDITY_DAY,
        )

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
    try:
        order_id = kite.place_order(
            tradingsymbol=trading_symbol,
            exchange=indices_zerodha_exchange.get(symbol),
            transaction_type=kite.TRANSACTION_TYPE_SELL,
            quantity=indices_lot_quantity.get(symbol) * quantity,
            variety=kite.VARIETY_REGULAR,
            order_type=kite.ORDER_TYPE_MARKET,
            product=kite.PRODUCT_NRML,
            validity=kite.VALIDITY_DAY,
        )

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


def get_zerodha_quote():
    current_td_instruments = filter(filter_instrument, instruments)
    symbol_list = [
        indices_zerodha_exchange.get(symbol) + ":" + inst["tradingsymbol"]
        for inst in current_td_instruments
    ]
    quote = kite.quote(symbol_list)

    ce_option_chain = {}
    pe_option_chain = {}
    for key, json_obj in quote.items():
        result = key.split(":")
        # Take the second part (index 1) as it contains everything after the colon
        trade_sym = result[1] if len(result) > 1 else key
        new_json_obj = {"ltp": json_obj["last_price"]}
        if trade_sym.endswith("CE") == True:
            ce_option_chain[trade_sym] = new_json_obj
        else:
            pe_option_chain[trade_sym] = new_json_obj

    return ce_option_chain, pe_option_chain, symbol


def filter_instrument(instrument):
    if (
        instrument["name"] == symbol.upper()
        and instrument["expiry"] == datetime.today().date()
    ):
        return True

    return False


# Setup one time data
today = datetime.today()
current_day = today.strftime("%A").upper()
symbol = indices_symbols.get(current_day)


kite = login_in_zerodha()

if kite:
    instruments = kite.instruments(exchange=indices_zerodha_exchange.get(symbol))
else:
    print("Zerodha Login failed.")
