# app/utils/error_handlers.py
from flask import jsonify

def handle_500_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500
