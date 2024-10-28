#!/usr/bin/env bash

PYTHON=python3
PIP=pip3

# Install required packages
${PIP} install -r requirements.txt || exit 1

# Generate a Django secret key
echo "SECRET_KEY=$(openssl rand -base64 100)" > .env

# Create table schemas
${PYTHON} manage.py makemigrations solax_registers || exit 1
${PYTHON} manage.py migrate || exit 1

# Create superuser credentials

if [ -z "${DJANGO_SUPERUSER_USERNAME}" ]; then
    read -p "Superuser name: " DJANGO_SUPERUSER_USERNAME
fi

if [ -z "${DJANGO_SUPERUSER_EMAIL}" ]; then
    read -p "Superuser email (optional): " DJANGO_SUPERUSER_EMAIL
fi

if [ -z "${DJANGO_SUPERUSER_PASSWORD}" ]; then
    read -p "Superuser password: " DJANGO_SUPERUSER_PASSWORD
fi

export DJANGO_SUPERUSER_USERNAME DJANGO_SUPERUSER_EMAIL DJANGO_SUPERUSER_PASSWORD
${PYTHON} manage.py createsuperuser --email "${DJANGO_SUPERUSER_EMAIL:-test@example.com}" --no-input || exit 1

# Collect the Django static files
${PYTHON} manage.py collectstatic || exit 1
