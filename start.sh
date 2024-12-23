#!/usr/bin/env bash

source .env

python3 manage.py makemigrations solax_registers || exit 1
python3 manage.py migrate || exit 1
REST_API_ADDRESS=${1:-"localhost"}:${2:-"8000"} gunicorn -c gunicorn_conf.py
