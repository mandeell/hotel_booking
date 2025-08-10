#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Navigate to the Django project directory
cd myhotel

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput