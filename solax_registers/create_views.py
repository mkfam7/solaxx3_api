from operator import attrgetter
from typing import Dict, List, Tuple, Type, Union

from django.db.models import Model

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView

from .constants import documentation, error, misc
from .utils import ResponseException, catch400, remove_keys, set_subtract


def create_views(
    upload_date_column: str,
    model_serializer: Type[ModelSerializer],
    last_record_model_serializer: Type[ModelSerializer],
    docs: List[Dict[str, str]],
    use_datetime: bool = True,
) -> Tuple[APIView]:
    """
    A function that returns a view.

    Parameters
    ----------
    upload_date_column : int
        column of model representing pushing date.
    model_serializer : rest_framework.serializers.ModelSerializer
        serializer of model.
    last_model_serializer : rest_framework.serializers.ModelSerializer
        serializer of the model keeping the last record.
    docs : dict
        documentation for the views. Example:
        ```python
    {
        "get": "Get minute stats records.",
        "post": "Push a minute stats record.",
        "delete": "Delete a minute stats record.",
    },
        ```
    """

    if use_datetime:
        get_parameters = documentation.GET_PARAMETERS
    else:
        get_parameters = documentation.GET_PARAMETERS_WITHOUT_DATETIME

    class StatsManager(APIView):
        model: Type[Model] = model_serializer.Meta.model
        last_record_model: Type[Model] = last_record_model_serializer.Meta.model

        @extend_schema(
            parameters=get_parameters,
            responses={
                200: model_serializer,
                400: OpenApiTypes.OBJECT,
                (500, "text/html"): OpenApiResponse(response=OpenApiTypes.ANY),
            },
            summary=docs["get"],
        )
        @catch400
        def get(self, request: Request) -> Response:
            query_params = request.query_params
            filter_range = (query_params.get("since"), query_params.get("before"))
            fields = query_params.getlist("fields") or self._get_model_fields()
            self._validate_for_extra_fields(fields)

            if filter_range != (None, None):
                return self._get_history_stats(
                    {"range": filter_range, "fields": fields}
                )
            return self._get_last_record_stats({"fields": fields})

        def _get_history_stats(self, config: dict) -> Response:
            filter_range, fields = config["range"], config["fields"]

            serialized_data = self._get_filtered_history_data(fields, filter_range)
            return Response(list(serialized_data.instance), status.HTTP_200_OK)

        def _validate_for_extra_fields(self, fields: list) -> list:
            model_fields = self._get_model_fields()
            extra_fields = set_subtract(fields, model_fields)
            if extra_fields:
                error_response = error.extra_fields_passed(extra_fields)
                raise ResponseException(error_response)

        def _get_model_fields(self) -> list:
            return list(map(attrgetter("name"), self.model._meta.get_fields()))

        def _get_filtered_history_data(
            self, stats: list, filter_range: list
        ) -> Type[ModelSerializer]:
            since, before = filter_range

            if self._is_no_timerange_specified(since, before):
                queryset = self.model.objects.all().values(*stats)
            else:
                queryset = self.model.objects.filter(
                    **self._construct_filter_params(since, before),
                ).values(*stats)

            serializer = model_serializer(queryset, many=True)
            return serializer

        def _construct_filter_params(
            self,
            since: Union[str, None],
            before: Union[str, None],
        ) -> Dict[str, str]:
            filter_params = {}
            if since is not None:
                filter_params[f"{upload_date_column}__gte"] = since
            if before is not None:
                filter_params[f"{upload_date_column}__lte"] = before

            return filter_params

        def _is_no_timerange_specified(
            self,
            since: Union[str, None],
            before: Union[str, None],
        ) -> bool:
            return (since, before) == (None, None)

        def _get_last_record_stats(self, config: dict) -> Response:
            fields = config["fields"]
            serializer = self._get_filtered_last_record_data(fields)
            serializer_content = list(serializer.instance)
            content_response = (
                {} if len(serializer_content) == 0 else serializer_content[0]
            )

            return Response(content_response, status.HTTP_200_OK)

        def _get_filtered_last_record_data(self, stats) -> Type[ModelSerializer]:
            queryset = self.last_record_model.objects.values(*stats)
            serializer = last_record_model_serializer(queryset, many=True)
            return serializer

        @extend_schema(
            summary=docs["post"],
            responses={
                201: model_serializer,
                400: OpenApiTypes.OBJECT,
                (500, "text/html"): OpenApiResponse(response=OpenApiTypes.ANY),
            },
            parameters=documentation.POST_PARAMETERS,
        )
        @catch400
        def post(self, request: Request) -> Response:
            overwrite = request.query_params.get("overwrite") or "false"
            self._validate_overwrite(overwrite)
            overwrite = overwrite == "true"

            payload = request.data
            self._validate_for_extra_fields_in_data(payload)
            self._post_last_record_stats(payload)
            return self._post_history_stats(payload, overwrite)

        def _validate_overwrite(self, overwrite: str) -> bool:
            if overwrite not in ("true", "false"):
                raise ResponseException(error.INVALID_FORCE_PARAM)

        def _validate_for_extra_fields_in_data(self, data: dict) -> list:
            given_fields = list(data.keys())
            self._validate_for_extra_fields(given_fields)

        def _post_history_stats(self, data: dict, overwrite: bool) -> Response:
            if overwrite:
                try:
                    primary_key_value = data[upload_date_column]
                    params_for_filter = {upload_date_column: primary_key_value}
                    self.model.objects.filter(**params_for_filter).delete()
                except KeyError:
                    pass

            serializer = model_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        def _post_last_record_stats(self, data: dict) -> Response:
            serializer = last_record_model_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            self.last_record_model.objects.update_or_create(defaults=data, id=1)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        @extend_schema(
            summary=docs["delete"],
            parameters=documentation.DELETE_PARAMS,
            responses={
                200: {"type": "object", "properties": {"deleted": {"type": "integer"}}},
                400: OpenApiTypes.OBJECT,
                (500, "text/html"): OpenApiResponse(response=OpenApiTypes.ANY),
            },
        )
        @catch400
        def delete(self, request: Request) -> Response:
            actions = {
                "delete_older_than": self._delete_older_than_date,
                "truncate": self._truncate,
            }
            action = request.query_params.get("action")
            args = request.query_params.getlist("args")
            self._validate_action(action, actions)

            return actions[action](args)

        def _delete_older_than_date(self, args: list) -> Response:
            if args == []:
                return error.MISSING_DATE_ARG

            date = args[0]

            filter_params = {f"{upload_date_column}__lte": date}
            queryset = self.model.objects.filter(**filter_params)

            no_deleted, _ = queryset.delete()
            return misc.deleted(no_deleted)

        def _truncate(self, args: list) -> Response:
            no_deleted, _ = self.model.objects.all().delete()
            return misc.deleted(no_deleted)

        def _validate_action(self, action: str, valid_actions):
            if not action:
                raise ResponseException(error.MISSING_ACTION_PARAM)

            if action not in valid_actions:
                raise ResponseException(error.INVALID_ACTION_PARAM)

    return StatsManager
