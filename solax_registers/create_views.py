from operator import attrgetter
from typing import Dict, List, Tuple, Type, Union

from django.db.models import Model

# from drf_spectacular.types import OpenApiTypes
# from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView

from .constants import documentation, error, misc
from .utils import remove_keys, set_subtract


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
    [
        # for history stats
        {
            "get": "Get minute stats records.",
            "post": "Push a minute stats record.",
            "delete": "Delete a minute stats record.",
        },
    ]
        ```
    """

    class StatsManager(APIView):
        model: Type[Model] = model_serializer.Meta.model
        last_record_model: Type[Model] = last_record_model_serializer.Meta.model

        def get(self, request: Request) -> Response:
            query_params = request.query_params
            filter_range = (query_params.get("since"), query_params.get("before"))
            fields = query_params.getlist("fields") or self._get_model_fields()
            if filter_range != (None, None):
                return self._get_history_stats(
                    {"range": filter_range, "fields": fields}
                )
            # return self._get_last_record_stats(request, {"fields": fields})

        def _get_history_stats(self, config: dict) -> Response:
            filter_range = config["range"]
            fields = config["fields"]

            extra_fields = self._get_extra_fields(fields)

            if extra_fields:
                return error.extra_fields_passed(extra_fields)

            serialized_data = self._get_filtered_history_data(fields, filter_range)
            return Response(list(serialized_data.instance), status.HTTP_200_OK)

        def _get_extra_fields(self, fields: list) -> list:
            model_fields = self._get_model_fields()
            return set_subtract(fields, model_fields)

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

        # def _get_last_record_stats(
        #     self, config: dict
        # ) -> Response:

    return StatsManager
