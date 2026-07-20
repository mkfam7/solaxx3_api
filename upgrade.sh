#!/usr/bin/env bash
python3 upgrade.py "$@" && \
python3 manage.py makemigrations solax_registers <<EOF
y
y
EOF