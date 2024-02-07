from datetime import datetime

# Get respective Symbol according to Weekday
indices_symbols = {
    "MONDAY": "midcpnifty",
    "TUESDAY": "finnifty",
    "WEDNESDAY": "banknifty",
    "THURSDAY": "nifty",
    "FRIDAY": "sensex",
}
indices_zerodha_exchange = {
    "midcpnifty": "NFO",
    "finnifty": "NFO",
    "banknifty": "NFO",
    "nifty": "NFO",
    "sensex": "BFO",
}
indices_trader_exchange = {
    "midcpnifty": "NSE",
    "finnifty": "NSE",
    "banknifty": "NSE",
    "nifty": "NSE",
    "sensex": "BSE",
}

indices_lot_quantity = {
    "midcpnifty": 40,
    "finnifty": 40,
    "banknifty": 15,
    "nifty": 50,
    "sensex": 10,
}

fyers_index_symbols = {
    "MONDAY": "MIDCPNIFTY",
    "TUESDAY": "FINNIFTY",
    "WEDNESDAY": "NIFTYBANK",
    "THURSDAY": "NIFTY50",
    "FRIDAY": "SENSEX",
}

def last_week_of_month(year, month, day):
    next_week = day + 7
    if next_week > 31:  # Assuming maximum days in a month as 31
        next_week -= 31
        if month == 12:  # If the current month is December, it's the last week
            return True
        else:
            return (
                datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
            ).day <= next_week
    return False


# Replace banknifty with Thursday if it's the last week of the month
today = datetime.today()
year = today.year
month = today.month
day = today.day

if last_week_of_month(year, month, day):
    indices_symbols["THURSDAY"] = "banknifty"

# Replace midcpnifty with Friday if it's the last week of the month
# if last_week_of_month(year, month, day):
#     indices_symbols["FRIDAY"] = "midcpnifty"

