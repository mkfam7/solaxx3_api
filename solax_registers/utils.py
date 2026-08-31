import datetime
from functools import wraps
import json
from operator import itemgetter
from os import environ
from string import ascii_lowercase
from typing import Any, Literal, Type

from django.contrib.auth.models import User
from django.db import models

COLUMN_CLASSES = {
    "positive_small_integer": models.PositiveSmallIntegerField,
    "small_integer": models.SmallIntegerField,
    "integer": models.IntegerField,
    "float": models.FloatField,
    "date": models.DateField,
    "datetime": models.DateTimeField,
}


class ResponseException(Exception):
    pass


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


def get_model_field_class(column_info: dict):
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

    column_info = _set_default_values(
        column_info,
        ["column_name", "column_type", "nullable", "length", "primary_key", "default"],
    )
    _validate_column_info(column_info)
    column_class = _get_column_class(column_info["column_type"])

    kwargs = {**column_info}
    kwargs.pop("column_name")
    kwargs.pop("column_type")
    _rename(kwargs, old="nullable", new="null")
    _rename(kwargs, old="length", new="max_length")
    kwargs = _remove_fields_with_defaults(kwargs)

    return column_class(**kwargs)


def get_fields_and_pk_name(columns):
    """
    Build a Django model field for each column, and identify the primary key.

    Parameters
    ----------
    columns : list[dict]
        Column definitions, as read from the columns file.

    Returns
    -------
    fields : dict[str, django.db.models.Field]
        Maps each column name to a fresh field instance for it.
    pk_name : str or None
        The name of the column marked `"primary_key": true`, if any.
    """

    fields = {}
    pk_name = None
    for column_info in columns:
        if column_info.get("primary_key") is True:
            pk_name = column_info["column_name"]
        fields[column_info["column_name"]] = get_model_field_class(column_info)

    return fields, pk_name


def get_fields_without_pk_flag(columns, pk_name):
    """
    Like `get_fields_and_pk_name`, but no column is built as a primary key.

    Used for the "last record" models, which always use Django's default
    `id` as their primary key and instead store the original primary-key
    column (named by `pk_name`) as an ordinary field.

    Parameters
    ----------
    columns : list[dict]
        Column definitions, as read from the columns file.
    pk_name : str or None
        The name of the column to build without its `primary_key` flag.

    Returns
    -------
    dict[str, django.db.models.Field]
        Maps each column name to a fresh field instance for it.
    """

    fields = {}
    for column_info in columns:
        if column_info["column_name"] == pk_name:
            column_info = {k: v for k, v in column_info.items() if k != "primary_key"}
        fields[column_info["column_name"]] = get_model_field_class(column_info)

    return fields


def _validate_column_info(column_info: dict):
    column_type = column_info.get("column_type", "N/A")
    _validate_column_type(column_type)

    is_null = column_info.get("nullable", "N/A")
    _validate_boolean(is_null, field_name="nullable")

    is_pk = column_info.get("primary_key", "N/A")
    _validate_boolean(is_pk, field_name="primary_key")

    length = column_info.get("length", "N/A")
    _validate_length(length)


def _validate_column_type(column_type):
    if column_type == "N/A":
        raise ValueError("Column type must be specified")

    if column_type not in COLUMN_CLASSES:
        choices = ", ".join(COLUMN_CLASSES.keys())
        raise ValueError(f"Column type should be one of: {choices}")


def _validate_boolean(value, field_name):
    if value not in (True, False, "N/A"):
        raise ValueError(f"{field_name} should be true, false or N/A")


def _validate_length(length: Any):
    if length != "N/A" and (not isinstance(length, int) or length < 1):
        raise ValueError("Invalid length; must be a positive number")


def _set_default_values(column_info: dict, args: list):
    result = {}
    for arg in args:
        result[arg] = column_info.get(arg, "N/A")
    return result


def _remove_fields_with_defaults(column_info: dict):
    result = {}
    for arg in column_info.keys():
        value = column_info[arg]
        if value != "N/A":
            result[arg] = value
    return result


def _get_column_class(column_type: str) -> Type[models.Model]:
    return COLUMN_CLASSES[column_type]


def _rename(d: dict, old: str, new: str) -> None:
    d[new] = d.pop(old)


def get_sample_column_values(
    column_info,
    pk,
    column_type_fallbacks=None,
    column_values=None,
    datetime_pk=True,
):
    """
    Build a dict of sample values for the given columns, for use in tests.

    Parameters
    ----------
    column_info : list[dict]
        Column definitions, as read from the columns file.
    pk : str
        The name of the primary key column.
    column_type_fallbacks : dict, optional
        Maps a column type to the sample value to use when no explicit
        value is given for a column of that type via `column_values`.
        Defaults to a fixed set of sample values per type.
    column_values : dict, optional
        Maps a column name to an explicit sample value, taking precedence
        over `column_type_fallbacks`. Defaults to no explicit overrides.
    datetime_pk : bool, optional
        Whether the primary key column is a datetime (True) or a plain
        date (False). Defaults to True.
    """

    if column_type_fallbacks is None:
        now = datetime.datetime.now()
        column_type_fallbacks = {
            "positive_small_integer": 0,
            "small_integer": -1,
            "integer": 0,
            "float": 0.6,
            "date": now.date(),
            "datetime": now,
        }
    if column_values is None:
        column_values = {}

    result = {}
    for column in column_info:
        name = column["column_name"]
        column_type = column["column_type"]

        if name in column_values:
            result[name] = column_values[name]

        elif column_type in column_type_fallbacks:
            result[name] = column_type_fallbacks[column_type]

    date_value = column_values.get(
        pk, "2022-01-01 00:00" if datetime_pk else "2022-01-01"
    )
    result[pk] = date_value
    return result


def read_columns_file():
    columns_file = environ.get("COLUMNS_FILE", "columns.json")

    with open(columns_file, encoding="utf-8") as f:
        columns = json.load(f)

    return columns


def get_a_nonexistent_column(index=0):
    letter = ascii_lowercase[index]
    columns_for_daily_stats = list(
        map(itemgetter("column_name"), read_columns_file()["daily_stats"])
    )
    nonexistent_column = columns_for_daily_stats[0]

    while (
        len(columns_for_daily_stats) != 0
        and nonexistent_column in columns_for_daily_stats
    ):
        nonexistent_column += letter

    if not columns_for_daily_stats:
        return "extra"
    return nonexistent_column


def catch400(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ResponseException as exc:
            return exc.args[0]

    return inner


def get_pk_for(model_or_serializer):
    """Return the primary key field of a model, or of a serializer's model."""
    try:
        return model_or_serializer._meta.pk
    except AttributeError:
        return model_or_serializer.Meta.model._meta.pk


def get_pk_name_for(model_or_serializer):
    return get_pk_for(model_or_serializer).name
