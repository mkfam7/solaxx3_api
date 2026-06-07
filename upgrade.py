#!/usr/bin/env python
"""
This is an upgrader script from version 2.0.2 to 2.0.3.

This variable may require the COLUMNS_FILE environment variable. If it
was not defined, the program resorts to "./columns.json".

Run this file in the root directory of the repository.
"""

import json
from os import environ
from operator import itemgetter

columns_file = environ.get("COLUMNS_FILE", "columns.json")

with open(columns_file, encoding="utf-8") as f:
    contents = json.load(f)


def getcolumns(key: str) -> list:
    return list(
        map(
            itemgetter("column_name"),
            contents[key],
        )
    )


if "upload_time" not in getcolumns("minute_stats"):
    contents["minute_stats"].insert(
        0,
        {
            "column_name": "upload_time",
            "column_type": "datetime",
            "primary_key": True,
        },
    )

if "upload_date" not in getcolumns("daily_stats"):
    contents["daily_stats"].insert(
        0,
        {
            "column_name": "upload_date",
            "column_type": "date",
            "primary_key": True,
        },
    )

print("Upgraded successfully to version 2.0.3")
