from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Additional configuration can be added here

# Import routes after creating the Flask app instance
from app.routes import strategy_route, telegram_route
