#!/usr/bin/env python
"""
This is an upgrader script from version 2.0.2 to 2.0.3.

This variable may require the COLUMNS_FILE environment variable. If it
was not defined, the program resorts to "./columns.json".

Run this file in the root directory of the repository.
"""

import json
from os import environ, get_terminal_size
from operator import itemgetter
from textwrap import fill
import sys

columns_file = environ.get("COLUMNS_FILE", "columns.json")
needs_an_upgrade = False

try:
    terminal_width = get_terminal_size().columns
except OSError:
    terminal_width = 80

with open(columns_file, encoding="utf-8") as f:
    contents = json.load(f)


def getcolumns(key: str) -> list:
    return list(
        map(
            itemgetter("column_name"),
            contents[key],
        )
    )


_ = lambda msg: fill(msg, width=terminal_width)

if "upload_time" not in getcolumns("minute_stats"):
    needs_an_upgrade = True
    contents["minute_stats"].insert(
        0,
        {
            "column_name": "upload_time",
            "column_type": "datetime",
            "primary_key": True,
        },
    )

if "upload_date" not in getcolumns("daily_stats"):
    needs_an_upgrade = True
    contents["daily_stats"].insert(
        0,
        {
            "column_name": "upload_date",
            "column_type": "date",
            "primary_key": True,
        },
    )

if not needs_an_upgrade:
    print("Nothing to do")
    sys.exit()

confirm = input(
    _("Are you sure you want to upgrade?")
    + "\n\n"
    + _(
        "This will only work if you did not change the names of the primary keys in solax_registers/models.py."
    )
    + "\n\n[y/N]> ",
)

if confirm not in ("y", "Y"):
    print("Aborted")
    sys.exit()

with open(columns_file, "w", encoding="utf-8") as f:
    json.dump(contents, f, indent=4)

print("Upgraded successfully to version 2.0.3")
