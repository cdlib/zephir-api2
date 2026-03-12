#!/bin/sh
curl -sf "http://localhost:${APP_PORT:-8000}/api/ping" > /dev/null
