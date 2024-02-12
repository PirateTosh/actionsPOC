from app import app
from app.utils.error_handlers import handle_500_error

# Register error handlers
app.register_error_handler(500, handle_500_error)

if __name__ == "__main__":
    print("starting server")
    app.run()
    # app.run(debug=True, threaded=True)
