import requests
from app.config import (
    TELEGRAM_API_BASE_URL,
    TELEGRAM_API_CHAT_ID,
    TELEGRAM_API_PARSE_MODE_MARKDOWN,
)


def telegram_send_message(chat_id, message):
    api_url = f"{TELEGRAM_API_BASE_URL}{TELEGRAM_API_CHAT_ID}{chat_id}{TELEGRAM_API_PARSE_MODE_MARKDOWN}{message}"
    response = requests.get(api_url)
    response_json = response.json()

    # Check if the message was sent successfully to this chat ID
    if response_json.get("ok"):
        response_data = {
            "success": True,
            "message": f"Message sent successfully to chat ID {chat_id}.",
        }
    else:
        response_data = {
            "success": False,
            "message": f"Failed to send message to chat ID {chat_id}.",
        }

    return response_data
