from typing import Literal

from django.contrib.auth.models import User
from django.db import models
from importlib import import_module


def has_user_permission(
    appname: str,
    model: models.Model,
    action: Literal["view", "add", "change", "delete"],
    user: User,
):
    model_name = model.__name__

    permission_string = appname + "." + action + "_" + model_name.lower()
    return user.has_perm(permission_string)


def set_subtract(a: list, b: list) -> list:
    """Subtract b from a as if they were `set`s."""
    diff = set(a) - set(b)
    return list(diff)


def create_field(name: str, **kwargs):
    if not hasattr(models, name):
        raise ImportError(f"Field {name!r} is not a valid field name")

    field_class = getattr(models, name)
    return field_class(**kwargs)
