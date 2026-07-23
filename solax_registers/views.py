from django.conf import settings
from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from .create_views import create_views
from .serializers import (
    DailyDetailsSerializer,
    DailyStatsSerializer,
    LastDayDetailsSerializer,
    LastDayStatsSerializer,
    LastMinuteStatsSerializer,
    MinuteStatsSerializer,
)

DailyStats = create_views(
    model_serializer=DailyStatsSerializer,
    last_record_model_serializer=LastDayStatsSerializer,
    docs={
        "get": "Get daily stats.",
        "post": "Add daily stats.",
        "delete": "Delete daily stats.",
    },
)


DailyDetails = create_views(
    model_serializer=DailyDetailsSerializer,
    last_record_model_serializer=LastDayDetailsSerializer,
    docs={
        "get": "Get daily stats, read minutely.",
        "post": "Add daily stats, read minutely.",
        "delete": "Delete daily stats, read minutely.",
    },
)

MinuteStats = create_views(
    model_serializer=MinuteStatsSerializer,
    last_record_model_serializer=LastMinuteStatsSerializer,
    docs={
        "get": "Get minute stats.",
        "post": "Add minute stats.",
        "delete": "Delete minute stats.",
    },
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


def index(request):
    version = settings.SPECTACULAR_SETTINGS["VERSION"]
    return render(request, "solax_registers/home.html", {"version": version})
