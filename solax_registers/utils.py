import json
from operator import itemgetter
from os import environ
from typing import Any, Literal, Type

from django.contrib.auth.models import User
from django.db import models
from string import ascii_lowercase


def has_user_permission(
    appname: str,
    model: models.Model,
    action: Literal["view", "add", "change", "delete"],
    user: User,
):
    """Check if a user has permission to perform a specified action."""

    model_name = model.__name__

    permission_string = appname + "." + action + "_" + model_name.lower()
    return user.has_perm(permission_string)


def set_subtract(a: list, b: list) -> list:
    """Subtract b from a as if they were `set`s."""
    diff = set(a) - set(b)
    return list(diff)


def parse_column_info(column_info: dict):
    """
    Return the appropriate Django field class for a column.

    Parameters
    ----------
    column_info : dict
        The information for a column.

    Raises
    ------
    ValueError
        This exception is raised if the information provided is invalid.
    """

    COLTYPE = "column_type"
    IS_NULL = "nullable"
    LENGTH = "length"
    COLUMN_CLASSES = {
        "positive_small_integer": models.PositiveSmallIntegerField,
        "small_integer": models.SmallIntegerField,
        "integer": models.IntegerField,
        "float": models.FloatField,
    }

    _validate_column_type(column_info[COLTYPE], COLUMN_CLASSES)
    _validate_column_nullable(column_info[IS_NULL])
    _validate_column_length(column_info[LENGTH])

    column_class = COLUMN_CLASSES[column_info[COLTYPE]]
    kwargs = {**column_info}
    kwargs["null"] = kwargs.pop("nullable")
    kwargs["max_length"] = kwargs.pop("length")
    kwargs = _filter_args(kwargs, ["null", "default", "max_length"])

    return column_class(**kwargs)


def _validate_column_type(column_type: Any, column_classes: dict):
    if column_type not in column_classes:
        error_msg = f"Invalid column type; must be {'or'.join(column_classes.keys())}"
        raise ValueError(error_msg)


def _validate_column_nullable(is_nullable: Any):
    if is_nullable != "N/A" and not isinstance(is_nullable, bool):
        raise ValueError("Invalid value for 'nullable' key; must be true, false, or 'N/A'")


def _validate_column_length(length: Any):
    if length != "N/A" and (not isinstance(length, int) or length < 1):
        raise ValueError("Invalid column length; must be a positive number")


def _filter_args(column_info: dict, args: list):
    result = {}
    for arg in args:
        value = column_info[arg]
        if value != "N/A":
            result[arg] = value
    return result


def remove_keys(dictionary, keys):
    copy_dict = {**dictionary}
    for key in keys:
        copy_dict.pop(key)
    return copy_dict


def get_sample_column_values(
    column_info,
    column_type_fallbacks={
        "positive_small_integer": 0,
        "small_integer": -1,
        "integer": 0,
        "float": 0.6,
    },
    column_values={},
    datetime_pk=True,
):
    result = {}
    for column in column_info:
        name = column["column_name"]
        column_type = column["column_type"]

        if name in column_values:
            result[name] = column_values[name]

        elif column_type in column_type_fallbacks:
            result[name] = column_type_fallbacks[column_type]

    date_column = "upload_time" if datetime_pk else "upload_date"
    date_value = column_values.get(date_column, "2022-01-01 00:00" if datetime_pk else "2022-01-01")
    result[date_column] = date_value
    return result


def read_columns_file():
    columns_file = environ.get("COLUMNS_FILE", "columns.json")

    with open(columns_file, encoding="utf-8") as f:
        columns = json.load(f)

    return columns


def get_a_nonexistent_column(index=0):
    letter = ascii_lowercase[index]
    columns_for_daily_stats = list(map(itemgetter("column_name"), read_columns_file()["daily_stats"]))
    nonexistent_column = columns_for_daily_stats[0]

    while len(columns_for_daily_stats) != 0 and nonexistent_column in columns_for_daily_stats:
        nonexistent_column += letter

    if not columns_for_daily_stats:
        return "extra"
    return nonexistent_column
