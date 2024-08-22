import os
import multiprocessing

APP_PORT = os.getenv("APP_PORT")
LOG_LEVEL = os.getenv("LOG_LEVEL")

worker_connections = 1000 # max number of simultaneous clients
worker_class = "gthread"
workers = 2 * multiprocessing.cpu_count() + 1
threads = 2
bind = f"0.0.0.0:{APP_PORT}"
wsgi_app = "app:create_app()"
loglevel = LOG_LEVEL