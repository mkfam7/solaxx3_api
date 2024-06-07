from operator import attrgetter
from typing import Dict, List, Tuple, Type, Union

from django.db.models import Model

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from .utils import set_subtract


def create_views(
    upload_date_column: str,
    model_serializer: Type[ModelSerializer],
    last_record_model_serializer: Type[ModelSerializer],
    docs: List[Dict[str, str]],
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

    STATS_PARAM = OpenApiParameter(
        name="stats",
        location="query",
        required=True,
        description="Stats to return.",
        style="form",
        explode=True,
        examples=[
            OpenApiExample(
                name="Ex. 1",
                summary="Using 'all'",
                value=["all"],
                description="You can use the word 'all' to return all stats.",
            ),
            OpenApiExample(
                name="Ex. 2",
                summary="Passing list of stats",
                value=["upload_time", "grid_voltage_r"],
                description="Finally, you can pass a list of stats.",
            ),
        ],
        many=True,
    )

    SINCE_PARAM = OpenApiParameter(
        name="since",
        type=(
            OpenApiTypes.DATETIME
            if upload_date_column.endswith("time")
            else OpenApiTypes.DATE
        ),
        location="query",
        required=False,
        description="First date in filter range. Optional.",
        style="form",
        explode=True,
        examples=[
            OpenApiExample(
                name="Ex. 1",
                summary="Example value",
                value="2023-01-01 00:00",
                description="You can use an ISO-8601 format to specify the datetime.",
            ),
            OpenApiExample(
                name="Ex. 2",
                summary="Another example value",
                value="2023-01-01",
                description="You can also pass an ISO-8601 date instead of datetime.",
            ),
        ],
    )

    BEFORE_PARAM = OpenApiParameter(
        name="before",
        type=(
            OpenApiTypes.DATETIME
            if upload_date_column.endswith("time")
            else OpenApiTypes.DATE
        ),
        location="query",
        required=False,
        description="Second date in filter range. Optional.",
        style="form",
        explode=True,
        examples=[
            OpenApiExample(
                name="Ex. 1",
                summary="Example value",
                value="2023-01-01 00:00",
                description="You can use an ISO-8601 format to specify the datetime.",
            ),
            OpenApiExample(
                name="Ex. 2",
                summary="Another example value",
                value="2023-01-01",
                description="You can also pass an ISO-8601 date instead of datetime.",
            ),
        ],
    )

    OVERWRITE_PARAM = OpenApiParameter(
        name="force",
        enum=["true", "false"],
        default="false",
        location="query",
        required=False,
        description=(
            "Pass 'force' to the query string to overwrite the record"
            " in the database, even though it exists."
        ),
        style="form",
        explode=True,
    )

    MISSING_STATS = Response(
        {"detail": "Query parameter 'stats' is mandatory."}, status.HTTP_400_BAD_REQUEST
    )

    extra_fields_passed = lambda f: Response(
        {"Some extra fields were passed:": f}, status.HTTP_400_BAD_REQUEST
    )

    GET_PARAMETERS = [STATS_PARAM, SINCE_PARAM, BEFORE_PARAM]

    POST_PARAMETERS = [OVERWRITE_PARAM]

    MODE_PARAM = OpenApiParameter(
        name="mode",
        enum=["delete_older_than", "truncate"],
        location="query",
        required=True,
        description="Parameter selecting which delete action to make.",
        style="form",
        explode=True,
        examples=[
            OpenApiExample(
                name="Ex. 1",
                value="delete_older_than",
                summary="Using delete_older_than",
                description="Use delete_older_than to delete records"
                " older than X date.",
            ),
            OpenApiExample(
                name="Ex. 2",
                value="truncate",
                summary="Using truncate",
                description="Use truncate to delete all history.",
            ),
        ],
    )

    ARGS_PARAM = OpenApiParameter(
        name="args",
        many=True,
        location="query",
        description="Parameter selecting which delete action to make.",
        style="form",
        explode=True,
    )

    DELETE_PARAMS = [MODE_PARAM, ARGS_PARAM]

    class ListAddDeleteStats(generics.ListCreateAPIView):
        serializer_class = model_serializer
        model: Type[Model] = model_serializer.Meta.model

        @extend_schema(
            parameters=GET_PARAMETERS,
            responses={
                200: model_serializer,
                400: OpenApiTypes.OBJECT,
                (500, "text/html"): OpenApiResponse(response=OpenApiTypes.ANY),
            },
            description=docs[0]["get"],
            summary=docs[0]["get"],
        )
        def get(self, request: Request) -> Response:
            """Get some data."""

            query_parameters = request.query_params

            since = query_parameters.get("since")
            before = query_parameters.get("before")
            filter_range = (since, before)

            stats = query_parameters.getlist("stats")
            extra_fields = self._return_extra_fields(stats)

            if len(stats) == 0:
                return MISSING_STATS

            if stats != ["all"] and extra_fields:
                return extra_fields_passed(extra_fields)

            serializer = self._get_filtered_data(stats, filter_range)
            return Response(list(serializer.instance), status.HTTP_200_OK)

        def _return_extra_fields(self, fields: list) -> list:
            model_fields = self._get_model_fields()
            return set_subtract(fields, model_fields)

        def _get_filtered_data(
            self, stats: list, filter_range: list
        ) -> Type[ModelSerializer]:
            since, before = filter_range

            if self._must_not_return_all_stats(stats):
                queryset = self.model.objects.filter(
                    **self._construct_filter_params(since, before)
                ).values(*stats)

            else:
                if self._is_no_timerange_specified(since, before):
                    queryset = self.model.objects.all().values()
                else:
                    queryset = self.model.objects.filter(
                        **self._construct_filter_params(since, before)
                    ).values()

            serializer = self.serializer_class(queryset, many=True)
            return serializer

        def _must_not_return_all_stats(self, stats: list) -> bool:
            return stats != ["all"]

        def _is_no_timerange_specified(
            self, since: Union[str, None], before: Union[str, None]
        ) -> bool:
            return (since, before) == (None, None)

        def _construct_filter_params(
            self, since: Union[str, None], before: Union[str, None]
        ) -> Dict[str, str]:
            filter_params = {}
            if since is not None:
                filter_params[f"{upload_date_column}__gte"] = since
            if before is not None:
                filter_params[f"{upload_date_column}__lte"] = before

            return filter_params

        @extend_schema(
            summary=docs[0]["post"],
            description=docs[0]["post"],
            responses={
                201: serializer_class,
                400: OpenApiTypes.OBJECT,
                (500, "text/html"): OpenApiResponse(response=OpenApiTypes.ANY),
            },
            parameters=POST_PARAMETERS,
        )
        def post(self, request: Request) -> Response:
            """Add some data."""

            force_create = request.query_params.get("force", "false")
            if not self._is_force_create_valid(force_create):
                MESSAGE = "'force' parameter must be either 'true' or 'false'"
                return Response({"detail": MESSAGE}, status.HTTP_400_BAD_REQUEST)

            overwrite = force_create == "true"

            extra_fields = self._return_extra_fields_in_data(request.data)
            if len(extra_fields) > 0:
                return extra_fields_passed(extra_fields)

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
            description=docs[0]["delete"],
            summary=docs[0]["delete"],
            parameters=DELETE_PARAMS,
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
            mode = request.query_params.get("mode")
            args = request.query_params.getlist("args")

            if not mode:
                MESSAGE = "Non-null query parameter 'mode' is mandatory."
                return Response({"detail": MESSAGE}, status.HTTP_400_BAD_REQUEST)

            if mode not in MODE_ACTION_MAPPING:
                MESSAGE = "Query parameter 'mode' is not among valid modes."
                return Response({"detail": MESSAGE}, status.HTTP_400_BAD_REQUEST)

            return MODE_ACTION_MAPPING[mode](args)

        def _delete_older_than_date(self, args: list) -> Response:
            if args == []:
                MESSAGE = "Argument 'date' in 'args' (0) is mandatory."
                return Response({"detail": MESSAGE}, status.HTTP_400_BAD_REQUEST)

            date = args[0]

            filter_params = {f"{upload_date_column}__lte": date}
            queryset = self.model.objects.filter(**filter_params)

            no_deleted, _ = queryset.delete()
            return Response({"deleted": no_deleted}, status.HTTP_200_OK)

        def _truncate(self, args: list) -> Response:
            no_deleted, _ = self.model.objects.all().delete()
            return Response({"deleted": no_deleted})

    class GetUpdateLastStats(generics.ListCreateAPIView):
        """Actions for the last record view."""

        serializer_class = last_record_model_serializer
        model: Type[Model] = serializer_class.Meta.model

        @extend_schema(
            parameters=[STATS_PARAM],
            responses={
                200: serializer_class,
                400: OpenApiTypes.OBJECT,
                (500, "text/html"): OpenApiResponse(response=OpenApiTypes.ANY),
            },
            description=docs[1]["get"],
            summary=docs[1]["get"],
        )
        def get(self, request: Request) -> Response:
            """Get some data."""

            query_params = request.query_params
            stats = query_params.getlist("stats")
            extra_fields = self._return_extra_fields(stats)

            if len(stats) == 0:
                MESSAGE = "Query parameter 'stats' is mandatory."
                return Response({"detail": MESSAGE}, status.HTTP_400_BAD_REQUEST)

            if stats != ["all"] and extra_fields:
                DATA = {"Some extra fields were passed:": extra_fields}
                return Response(DATA, status.HTTP_400_BAD_REQUEST)

            serializer = self._get_data(stats)
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
            description=docs[1]["post"],
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
                DATA = {"Some extra fields were passed:": extra_fields}
                return Response(DATA, status.HTTP_400_BAD_REQUEST)

            self.model.objects.all().delete()
            return super().post(request)

        def _return_extra_fields_in_data(self, data: dict) -> list:
            given_fields = list(data.keys())
            extras = self._return_extra_fields(given_fields)
            return extras

        def _get_model_fields(self) -> list:
            return list(map(attrgetter("name"), self.model._meta.get_fields()))

    return ListAddDeleteStats, GetUpdateLastStats
