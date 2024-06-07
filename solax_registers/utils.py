from typing import Literal

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
