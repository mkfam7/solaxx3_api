from operator import attrgetter
from typing import Dict, List, Tuple, Type, Union

from django.db.models import Model
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from .constants import documentation, error
from .utils import set_subtract


def create_views(
    upload_date_column: str,
    model_serializer: Type[ModelSerializer],
    last_record_model_serializer: Type[ModelSerializer],
    docs: List[Dict[str, str]],
    use_datetime: bool = True,
) -> Tuple[generics.ListCreateAPIView]:
    """A function that returns two views.
    Parameters:

    :param upload_date_column: column of model representing pushing date.
    :param model_serializer: serializer of model.
    :param last_model_serializer: serializer of the model keeping the last record.
    :param docs: documentation for the views. Example:
        ```python
    [
        # for history stats
        {
            "get": "Get minute stats.",
            "post": "Push minute stats.",
            "delete": "Delete minute stats.",
        },
        # for last record stats
        {
            "get": "Get last minute stats.",
            "post": "Push minute stats.",
        }
    ]
        ```
    """

    if use_datetime:
        get_parameters = documentation.GET_PARAMETERS
    else:
        get_parameters = documentation.GET_PARAMETERS_WITHOUT_DATETIME

    class ListAddDeleteStats(generics.ListCreateAPIView):
        serializer_class = model_serializer
        model: Type[Model] = model_serializer.Meta.model

        @extend_schema(
            parameters=get_parameters(upload_date_column),
            responses={
                200: model_serializer,
                400: OpenApiTypes.OBJECT,
                (500, "text/html"): OpenApiResponse(response=OpenApiTypes.ANY),
            },
            summary=docs[0]["get"],
        )
        def get(self, request: Request) -> Response:
            """Get some data."""

            query_parameters = request.query_params
            since = query_parameters.get("since")
            before = query_parameters.get("before")
            filter_range = (since, before)
            fields = query_parameters.getlist("fields")

            extra_fields = self._return_extra_fields(fields)
            if len(fields) == 0:
                return error.MISSING_FIELDS

            if fields != ["all"] and extra_fields:
                return error.extra_fields_passed(extra_fields)

            serializer = self._get_filtered_data(fields, filter_range)
            return Response(list(serializer.instance), status.HTTP_200_OK)

        def _return_extra_fields(self, fields: list) -> list:
            model_fields = self._get_model_fields()
            return set_subtract(fields, model_fields)

        def _get_filtered_data(self, stats: list, filter_range: list) -> Type[ModelSerializer]:
            since, before = filter_range

            if self._must_not_return_all_stats(stats):
                queryset = self.model.objects.filter(
                    **self._construct_filter_params(since, before),
                ).values(*stats)

            elif self._is_no_timerange_specified(since, before):
                queryset = self.model.objects.all().values()
            else:
                queryset = self.model.objects.filter(
                    **self._construct_filter_params(since, before),
                ).values()

            serializer = self.serializer_class(queryset, many=True)
            return serializer

        def _must_not_return_all_stats(self, stats: list) -> bool:
            return stats != ["all"]

        def _is_no_timerange_specified(
            self,
            since: Union[str, None],
            before: Union[str, None],
        ) -> bool:
            return (since, before) == (None, None)

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

        @extend_schema(
            summary=docs[0]["post"],
            responses={
                201: serializer_class,
                400: OpenApiTypes.OBJECT,
                (500, "text/html"): OpenApiResponse(response=OpenApiTypes.ANY),
            },
            parameters=documentation.POST_PARAMETERS,
        )
        def post(self, request: Request) -> Response:
            """Add some data."""

            force_create = request.query_params.get("overwrite", "false")
            if not self._is_force_create_valid(force_create):
                return error.INVALID_FORCE_PARAM

            overwrite = force_create == "true"

            extra_fields = self._return_extra_fields_in_data(request.data)
            if extra_fields:
                return error.extra_fields_passed(extra_fields)

            if overwrite:
                primary_key_value = request.data[upload_date_column]
                params_for_filter = {upload_date_column: primary_key_value}
                self.model.objects.filter(**params_for_filter).delete()

            return super().post(request)

        def _is_force_create_valid(self, force_create: str) -> bool:
            return force_create in ("true", "false")

        def _return_extra_fields_in_data(self, data: dict) -> list:
            given_fields = list(data.keys())
            extras = self._return_extra_fields(given_fields)
            return extras

        def _get_model_fields(self) -> list:
            return list(map(attrgetter("name"), self.model._meta.get_fields()))

        @extend_schema(
            summary=docs[0]["delete"],
            parameters=documentation.DELETE_PARAMS,
            responses={
                200: {"type": "object", "properties": {"deleted": {"type": "integer"}}},
                400: OpenApiTypes.OBJECT,
                (500, "text/html"): OpenApiResponse(response=OpenApiTypes.ANY),
            },
        )
        def delete(self, request: Request) -> Response:
            MODE_ACTION_MAPPING = {
                "delete_older_than": self._delete_older_than_date,
                "truncate": self._truncate,
            }
            action = request.query_params.get("action")
            args = request.query_params.getlist("args")

            if not action:
                return error.MISSING_ACTION_PARAM

            if action not in MODE_ACTION_MAPPING:
                return error.INVALID_ACTION_PARAM

            return MODE_ACTION_MAPPING[action](args)

        def _delete_older_than_date(self, args: list) -> Response:
            if args == []:
                return error.MISSING_DATE_ARG

            date = args[0]

            filter_params = {f"{upload_date_column}__lte": date}
            queryset = self.model.objects.filter(**filter_params)

            no_deleted, _ = queryset.delete()
            return error.deleted(no_deleted)

        def _truncate(self, args: list) -> Response:
            no_deleted, _ = self.model.objects.all().delete()
            return error.deleted(no_deleted)

    class GetUpdateLastStats(generics.ListCreateAPIView):
        """Actions for the last record view."""

        serializer_class = last_record_model_serializer
        model: Type[Model] = serializer_class.Meta.model

        @extend_schema(
            parameters=[documentation.STATS_PARAM],
            responses={
                200: serializer_class,
                400: OpenApiTypes.OBJECT,
                (500, "text/html"): OpenApiResponse(response=OpenApiTypes.ANY),
            },
            summary=docs[1]["get"],
        )
        def get(self, request: Request) -> Response:
            """Get some data."""

            query_params = request.query_params
            fields = query_params.getlist("fields")
            extra_fields = self._return_extra_fields(fields)

            if len(fields) == 0:
                return error.MISSING_FIELDS

            if fields != ["all"] and extra_fields:
                return error.extra_fields_passed(extra_fields)

            serializer = self._get_data(fields)
            return Response(list(serializer.instance)[0], status.HTTP_200_OK)

        def _return_extra_fields(self, fields: list) -> list:
            model_fields = self._get_model_fields()
            return set_subtract(fields, model_fields)

        def _get_data(self, stats) -> Type[ModelSerializer]:
            if self._must_not_return_all_stats(stats):
                queryset = self.model.objects.values(*stats)
            else:
                queryset = self.model.objects.values()

            serializer = self.serializer_class(queryset, many=True)
            return serializer

        def _must_not_return_all_stats(self, stats: list) -> bool:
            return stats != ["all"]

        @extend_schema(
            summary=docs[1]["post"],
            responses={
                201: serializer_class,
                400: OpenApiTypes.OBJECT,
                (500, "text/html"): OpenApiResponse(response=OpenApiTypes.ANY),
            },
        )
        def post(self, request: Request) -> Response:
            """Post some data."""

            extra_fields = self._return_extra_fields_in_data(request.data)
            if len(extra_fields) > 0:
                return error.extra_fields_passed(extra_fields)

            self.model.objects.all().delete()
            return super().post(request)

        def _return_extra_fields_in_data(self, data: dict) -> list:
            given_fields = list(data.keys())
            extras = self._return_extra_fields(given_fields)
            return extras

        def _get_model_fields(self) -> list:
            return list(map(attrgetter("name"), self.model._meta.get_fields()))

    return ListAddDeleteStats, GetUpdateLastStats
