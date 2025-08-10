#!/usr/bin/env bash

# Navigate to the Django project directory
cd myhotel

# Start the Gunicorn server
gunicorn --bind 0.0.0.0:$PORT --workers 3 --timeout 120 myhotel.wsgi:application