from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from .create_views import create_views
from .serializers import DailyStatsSerializer, LastDayStatsSerializer, LastMinuteStatsSerializer, MinuteStatsSerializer

ListAddMinuteStats, GetUpdateLastMinuteStats = create_views(
    upload_date_column="upload_time",
    model_serializer=MinuteStatsSerializer,
    last_record_model_serializer=LastMinuteStatsSerializer,
    docs=[
        {
            "get": "Get minute stats.",
            "post": "Add minute stats.",
            "delete": "Delete minute stats.",
        },
        {
            "get": "Get last minute stats.",
            "post": "Push minute stats.",
        },
    ],
)
ListAddDailyStats, GetUpdateLastDayStats = create_views(
    upload_date_column="upload_date",
    model_serializer=DailyStatsSerializer,
    last_record_model_serializer=LastDayStatsSerializer,
    docs=[
        {
            "get": "Get daily stats.",
            "post": "Add daily stats.",
            "delete": "Delete daily stats.",
        },
        {
            "get": "Get last day stats.",
            "post": "Push last day stats.",
        },
    ],
)


class Healthz(ListAPIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: OpenApiTypes.STR},
        examples=[OpenApiExample(name="Success", value="healthy")],
        summary="A healthy check endpoint",
    )
    def get(self, _):
        return Response("healthy", HTTP_200_OK)
