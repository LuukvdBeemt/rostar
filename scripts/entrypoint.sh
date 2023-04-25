#!/bin/sh

# If anything goes wrong, exit with error code 0
set -e

python -u /app/main.py

crond -f