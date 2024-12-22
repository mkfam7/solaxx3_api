#!/usr/bin/env bash

host=${1:-"localhost"}
port=${2:-"8000"}

source .env

python3 manage.py makemigrations solax_registers || exit 1
python3 manage.py migrate || exit 1
gunicorn -c gunicorn_conf.py
