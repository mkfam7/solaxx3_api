#!/usr/bin/env bash

host=${1:-"localhost"}
port=${2:-"8000"}

python3 manage.py runserver ${host}:${port}