from typing import Any, Literal, Type

from django.contrib.auth.models import User
from django.db import models


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
    CHOICES = "choices"
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
    kwargs = _filter_args(kwargs, ["null", "default", "max_length", CHOICES])

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
