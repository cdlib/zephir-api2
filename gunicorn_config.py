import os

APP_PORT = os.getenv("APP_PORT", 8000)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

bind = f"0.0.0.0:{APP_PORT}"
wsgi_app = "app:create_app()"
loglevel = LOG_LEVEL

accesslog = "-"
errorlog = "-"