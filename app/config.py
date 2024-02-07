DEBUG_MODE = True

# Fyers Details
FYERS_ID = "XV30279"
APP_ID = "2"  # Value 2 is used for web login
CLIENT_ID = "9HEI4IDQEK-100"
APP_SECRET = "494K0HOB2C"
REDIRECT_URI = "https://trade.fyers.in/api-login/redirect-uri/index.html"
TOTP_KEY = "YWLD6PGLM3JCMW2QBBJ3AWUKCMVQT3U3"
PIN = 9999
APP_ID_HASH = "0273fdb25e81e790585f43c0b5fe2a3d332988086bfe45f7850e2d9629dd52d0"
# Zerodha Details
ZERODHA_API_KEY = ""
ZERODHA_API_SECRET = ""
ZERODHA_USER_ID = ""
ZERODHA_USER_PWD = ""
ZERODHA_TOTP_KEY = ""

# API endpoints
BASE_URL = "https://api-t2.fyers.in/vagator/v2"
BASE_URL_2 = "https://api-t1.fyers.in/api/v3"
URL_SEND_LOGIN_OTP = BASE_URL + "/send_login_otp_v2"
URL_VERIFY_TOTP = BASE_URL + "/verify_otp"
URL_VERIFY_PIN = BASE_URL + "/verify_pin_v2"
URL_TOKEN = BASE_URL_2 + "/token"

SUCCESS = 1
ERROR = -1

# POSTGRES LOGIN DETAILS:
DATABASE_URL = "host=localhost port=5432 dbname=postgres user=postgres password=xorSprinters@8 sslmode=prefer connect_timeout=10"


# TELEGRAM:
BOT_TOKEN = ""
TELEGRAM_API_BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?"
TELEGRAM_API_CHAT_ID = "chat_id="
TELEGRAM_API_PARSE_MODE_MARKDOWN = "&parse_mode=MarkdownV2&text="
