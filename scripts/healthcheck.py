import os
import sys
import urllib.request

port = os.environ.get("APP_PORT", "8000")

try:
    urllib.request.urlopen(f"http://localhost:{port}/api/ping", timeout=5)
except Exception:
    sys.exit(1)
