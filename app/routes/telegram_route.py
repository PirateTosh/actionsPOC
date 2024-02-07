from flask import request, jsonify
from app import app
from app.services import telegram_service
from app.utils.validation import validate_telegram_send_message_params


@app.route("/telegram/send_message", methods=["POST"])
def telegram_bot_sendmessage():
    try:
        data = request.get_json()
        chat_ids, message = validate_telegram_send_message_params(data)
        response_data = telegram_service.telegram_send_message(chat_ids, message)
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
