import datetime as dt

from flask import abort

def validate_date(date_str):
    try:
        return dt.datetime.strptime(date_str, "%d-%m-%Y").date()
    except ValueError:
        return None
    
def validate_get_history_params(data):
    required_params = ['resolution', 'no_of_candles', 'end_date', 'symbol']
    for param in required_params:
        if param not in data:
            abort(400, description=f'Missing required parameter: {param}')
                
    resolution = data.get('resolution')
    # start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    symbol = data.get('symbol')
    period_str = data.get('no_of_candles')
    
    # Validate resolution
    if resolution not in [1, 5, 15, 60, 240]:
        abort(400, description='Invalid resolution parameter. Please provide a valid resolution (1, 5, 15, 60, 240).')
    
    # # Validate start_date
    # start_date = validate_date(start_date_str)
    # if start_date is None:
    #     abort(400, description='Invalid or missing start date parameter. Please enter the date in DD-MM-YYYY format.')
    
    # Validate end_date
    end_date = validate_date(end_date_str)
    if end_date is None:
        abort(400, description='Invalid or missing end date parameter. Please enter the date in DD-MM-YYYY format.')
    
    # Validate symbol (supporting only NIFTY50)
    if symbol is None:
        abort(400, description='Invalid or missing symbol parameter. Currently supporting only NIFTY50.')

    return resolution, end_date, symbol, period_str

def validate_telegram_send_message_params(data):
    # Validate that 'chat_ids' and 'message' parameters are present in the request body
    if 'chat_ids' not in data or 'message' not in data:
        raise ValueError("Both 'chat_ids' and 'message' parameters are required.")

    chat_ids = data.get('chat_ids', [])
    message = data.get('message', '')

    # Ensure chat_ids is a non-empty list
    if not isinstance(chat_ids, list) or not chat_ids:
        raise ValueError("'chat_ids' must be a non-empty list.")
    
    # Ensure message is a non-empty string
    if not isinstance(message, str) or not message.strip():
        raise ValueError("'message' must be a non-empty string.")
    
    escaped_message = escape_telegram_reserved_chars(message)
                      
    return chat_ids, escaped_message

def escape_telegram_reserved_chars(message):
    # Reserved characters in Telegram: . ! ( ) + - = > | { } [ ] " ' ` * _ ~ # `
    reserved_chars = ['.', '!', '(', ')', '+', '-', '=', '>', '|', '{', '}', '[', ']', '"', "'", '`', '*', '_', '~', '#', '`']
    
    # Escape each reserved character in the message
    escaped_message = message
    for char in reserved_chars:
        escaped_message = escaped_message.replace(char, f'\\{char}')

    return escaped_message