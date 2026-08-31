"""
Business logic for reading, writing, and deleting inverter stats records.

Kept separate from the view/request-handling code in `create_views.py` so it
can be reasoned about independently of Django's request/response cycle. Each
function here corresponds to one piece of what `StatsManager` used to do
directly as a private method.
"""

from operator import attrgetter
from typing import Dict, List, Type, Union

from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from .constants import response_templates
from .utils import ResponseException, set_subtract


def get_model_field_names(model) -> List[str]:
    """Return the names of every field on a model."""
    return list(map(attrgetter("name"), model._meta.get_fields()))


def validate_no_extra_fields(fields: List[str], model) -> None:
    """Raise ResponseException if `fields` contains names not on `model`."""
    model_fields = get_model_field_names(model)
    extra_fields = set_subtract(fields, model_fields)
    if extra_fields:
        error_response = response_templates.extra_fields_passed(extra_fields)
        raise ResponseException(error_response)


def _is_no_timerange_specified(
    since: Union[str, None], before: Union[str, None]
) -> bool:
    return (since, before) == (None, None)


def _construct_date_filter_params(
    pk_column: str, since: Union[str, None], before: Union[str, None]
) -> Dict[str, str]:
    filter_params = {}
    if since is not None:
        filter_params[f"{pk_column}__gte"] = since
    if before is not None:
        filter_params[f"{pk_column}__lte"] = before
    return filter_params


def get_history_stats(
    model,
    model_serializer: Type[ModelSerializer],
    pk_column: str,
    fields: List[str],
    since: Union[str, None],
    before: Union[str, None],
) -> Response:
    """Handle a GET request that specifies a `since` and/or `before` filter."""
    if _is_no_timerange_specified(since, before):
        queryset = model.objects.all().values(*fields)
    else:
        queryset = model.objects.filter(
            **_construct_date_filter_params(pk_column, since, before)
        ).values(*fields)

    serializer = model_serializer(queryset, many=True)
    return Response(list(serializer.instance), status.HTTP_200_OK)


def get_last_record_stats(
    last_record_model,
    last_record_model_serializer: Type[ModelSerializer],
    fields: List[str],
) -> Response:
    """Handle a GET request with no date filter: return the single last record."""
    queryset = last_record_model.objects.values(*fields)
    serializer = last_record_model_serializer(queryset, many=True)
    serializer_content = list(serializer.instance)
    content_response = {} if len(serializer_content) == 0 else serializer_content[0]
    return Response(content_response, status.HTTP_200_OK)


def validate_overwrite_param(overwrite: str) -> bool:
    """Validate the `overwrite` query param string and return it as a bool."""
    if overwrite not in ("true", "false"):
        raise ResponseException(response_templates.INVALID_FORCE_PARAM)
    return overwrite == "true"


def save_history_record(
    model,
    model_serializer: Type[ModelSerializer],
    data: dict,
    pk_column: str,
    overwrite: bool,
) -> Response:
    """
    Validate and save a new history record.

    If `overwrite`, first deletes any existing record with the same primary
    key as `data`. If `data` has no value for the primary key column, this
    step is silently skipped (serializer validation below will reject the
    record for the actual missing-primary-key reason).
    """
    if overwrite:
        try:
            primary_key_value = data[pk_column]
            model.objects.filter(**{pk_column: primary_key_value}).delete()
        except KeyError:
            pass

    serializer = model_serializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def save_last_record(
    last_record_model,
    last_record_model_serializer: Type[ModelSerializer],
    data: dict,
) -> None:
    """Validate `data` and upsert the single 'last record' row (always id=1)."""
    serializer = last_record_model_serializer(data=data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data
    last_record_model.objects.update_or_create(defaults=validated_data, id=1)


def validate_action_param(action, valid_actions) -> None:
    """Raise ResponseException if `action` is missing or not a valid choice."""
    if not action:
        raise ResponseException(response_templates.MISSING_ACTION_PARAM)
    if action not in valid_actions:
        raise ResponseException(response_templates.INVALID_ACTION_PARAM)


def delete_older_than(model, pk_column: str, args: List[str]) -> Response:
    """Delete all records with `pk_column` <= the date given as the first arg."""
    if args == []:
        return response_templates.MISSING_DATE_ARG

    date = args[0]
    queryset = model.objects.filter(**{f"{pk_column}__lte": date})
    no_deleted, _ = queryset.delete()
    return response_templates.deleted(no_deleted)


def truncate(model, pk_column: str, args: List[str]) -> Response:
    """
    Delete all records for `model`.

    `pk_column` and `args` are accepted but unused, so this has the same
    call signature as `delete_older_than` and both can be dispatched from
    a single `{action_name: function}` mapping.
    """
    no_deleted, _ = model.objects.all().delete()
    return response_templates.deleted(no_deleted)
