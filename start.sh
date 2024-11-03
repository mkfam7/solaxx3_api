#!/usr/bin/env bash

host=${1:-"localhost"}
port=${2:-"8000"}

source .env
python3 manage.py runserver ${host}:${port}