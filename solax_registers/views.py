from .create_views import create_views
from .serializers import *

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
