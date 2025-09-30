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
from .utils import remove_keys, set_subtract


def create_views(
    upload_date_column: str,
    model_serializer: Type[ModelSerializer],
    last_record_model_serializer: Type[ModelSerializer],
    docs: List[Dict[str, str]],
    use_datetime: bool = True,
) -> Tuple[generics.ListCreateAPIView]:
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
