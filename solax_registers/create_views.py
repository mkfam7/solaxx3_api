from typing import Dict, Type

from django.db.models import DateField
from django.db.models import Model
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView

from . import services
from .constants import documentation
from .utils import catch400, get_pk_name_for


def create_views(
    model_serializer: Type[ModelSerializer],
    last_record_model_serializer: Type[ModelSerializer],
    docs: Dict[str, str],
) -> APIView:
    """
    A function that returns a view.

    Parameters
    ----------
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

    use_datetime = not isinstance(model_serializer.Meta.model._meta.pk, DateField)
    upload_date_column = get_pk_name_for(model_serializer)
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
            since = query_params.get("since")
            before = query_params.get("before")
            fields = query_params.getlist(
                "fields"
            ) or services.get_model_field_names(self.model)
            services.validate_no_extra_fields(fields, self.model)

            if (since, before) != (None, None):
                return services.get_history_stats(
                    self.model,
                    model_serializer,
                    upload_date_column,
                    fields,
                    since,
                    before,
                )
            return services.get_last_record_stats(
                self.last_record_model, last_record_model_serializer, fields
            )

        @extend_schema(
            summary=docs["post"],
            request=model_serializer,
            responses={
                201: model_serializer,
                400: OpenApiTypes.OBJECT,
                (500, "text/html"): OpenApiResponse(response=OpenApiTypes.ANY),
            },
            parameters=documentation.POST_PARAMETERS,
        )
        @catch400
        def post(self, request: Request) -> Response:
            overwrite = services.validate_overwrite_param(
                request.query_params.get("overwrite") or "false"
            )

            payload = request.data
            services.validate_no_extra_fields(list(payload.keys()), self.model)
            services.save_last_record(
                self.last_record_model, last_record_model_serializer, payload
            )
            return services.save_history_record(
                self.model, model_serializer, payload, upload_date_column, overwrite
            )

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
                "delete_older_than": services.delete_older_than,
                "truncate": services.truncate,
            }
            action = request.query_params.get("action")
            args = request.query_params.getlist("args")
            services.validate_action_param(action, actions)

            return actions[action](self.model, upload_date_column, args)

    return StatsManager
