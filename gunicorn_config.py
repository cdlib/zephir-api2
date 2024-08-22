import os

APP_PORT = os.getenv("APP_PORT")
LOG_LEVEL = os.getenv("LOG_LEVEL")

bind = f"0.0.0.0:{APP_PORT}"
wsgi_app = "app:create_app()"
loglevel = LOG_LEVEL