#!/usr/bin/env python
"""
This is an upgrader script from version 2.0.2 to 2.1.0.

This variable may require the COLUMNS_FILE environment variable. If it
was not defined, the program resorts to "./columns.json".

Run this file in the root directory of the repository.

This script will do nothing without your explicit approval.
"""

import json
from os import environ, get_terminal_size
from operator import itemgetter
from textwrap import fill
import sys
from argparse import ArgumentParser

columns_file = environ.get("COLUMNS_FILE", "columns.json")


def get_term_size():
    try:
        return get_terminal_size().columns
    except OSError:
        return 80


def getcolumns(key: str, contents) -> list:
    return list(
        map(
            itemgetter("column_name"),
            contents[key],
        )
    )


def get_column_index(l, column_name):
    for idx, col in enumerate(l):
        if col["column_name"] == column_name:
            return idx


def _get_contents():
    columns_file = environ.get("COLUMNS_FILE", "columns.json")
    with open(columns_file, encoding="utf-8") as f:
        return json.load(f)


def _write_contents(contents):
    with open(columns_file, "w", encoding="utf-8") as f:
        json.dump(contents, f, indent=2)


def _(msg):
    return fill(msg, width=terminal_width)


def abort_if_needed(confirm_value):
    if confirm_value not in (True, "y"):
        print("Aborted", file=sys.stderr)
        sys.exit(130)


def confirm(prompt):
    c = auto_confirm or input(prompt).lower()
    abort_if_needed(c)


def _is_add_pk_upgrade_needed():
    contents = _get_contents()
    columns_minute_stats = getcolumns("minute_stats", contents)
    columns_daily_stats = getcolumns("daily_stats", contents)

    return (
        "upload_time" not in columns_minute_stats
        and "upload_date" not in columns_daily_stats
    )


def _do_add_pk_upgrade():
    contents = _get_contents()
    contents["minute_stats"].insert(
        0,
        {
            "column_name": "upload_time",
            "column_type": "datetime",
            "primary_key": True,
        },
    )
    contents["daily_stats"].insert(
        0,
        {
            "column_name": "upload_date",
            "column_type": "date",
            "primary_key": True,
        },
    )

    _write_contents(contents)


def _is_rename_upload_time_upgrade_needed():
    contents = _get_contents()
    columns = getcolumns("minute_stats", contents)
    return "upload_time" in columns


def info(*args, **kwargs):
    if not auto_confirm:
        print(*args, **kwargs)


def _do_rename_upload_time_upgrade():
    contents = _get_contents()
    pk_index = get_column_index(contents["minute_stats"], "upload_time")
    contents["minute_stats"][pk_index]["column_name"] = "upload_datetime"
    _write_contents(contents)


terminal_width = get_term_size()
a = ArgumentParser()
a.add_argument(
    "-f",
    "--force",
    action="store_true",
    help="Whether to confirm all operations and suppress any user prompts.",
)
args = a.parse_args()
auto_confirm = args.force

needs_an_upgrade = (
    _is_add_pk_upgrade_needed() or _is_rename_upload_time_upgrade_needed()
)
if needs_an_upgrade:
    confirm("Are you sure you want to upgrade? You will be prompted before each \
upgrade action needed. [y/N] ")


needs_an_upgrade = _is_add_pk_upgrade_needed()
if needs_an_upgrade:
    info(
        "\n"
        + _("""\
Starting with this version, it is required to include the primary key into the
columns file and add it a field of '"primary_key": true'. Would you like to:""")
        + """
- add primary key "upload_time" to "minute_stats", and
- add primary key "upload_date" to "daily_stats"?
"""
    )
    confirm("[y/N] ")
    _do_add_pk_upgrade()
    info("Done!")

needs_an_upgrade = _is_rename_upload_time_upgrade_needed()

if not needs_an_upgrade:
    print("Nothing to do")
    sys.exit()

prompt = "Would you like to rename minute_stats 'upload_time' to \
'upload_datetime'? This action is not required. [y/N] "


confirm(prompt)

_do_rename_upload_time_upgrade()
print("Successfully upgraded to version 2.1.0!")
