from app.services.backtesting_service import get_backtesting_quote
from app.services.zerodha_service import get_zerodha_quote, place_zerodha_order
from app.services.fyers_service import get_fyers_quote, place_fyers_order


def get_quote(userType, date):
    if userType == "Fyers":
        return get_fyers_quote()

    elif userType == "Backtesting":
        return get_backtesting_quote(date)

    else:
        return get_zerodha_quote()


def place_order(userType, trade_symbol, isExit):
    if userType == "Fyers":
        return place_fyers_order(trade_symbol, isExit)
    else:
        return place_zerodha_order(trade_symbol, isExit)
