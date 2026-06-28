from rest_framework.serializers import ModelSerializer

from .models import (
    DailyDetailsRecord,
    DailyStatsRecord,
    LastDayDetailsRecord,
    LastDayStatsRecord,
    LastMinuteStatsRecord,
    MinuteStatsRecord,
)


class DailyStatsSerializer(ModelSerializer):
    class Meta:
        model = DailyStatsRecord
        fields = "__all__"


class MinuteStatsSerializer(ModelSerializer):
    class Meta:
        model = MinuteStatsRecord
        fields = "__all__"


class LastMinuteStatsSerializer(ModelSerializer):
    class Meta:
        model = LastMinuteStatsRecord
        exclude = ("id",)


class LastDayStatsSerializer(ModelSerializer):
    class Meta:
        model = LastDayStatsRecord
        exclude = ("id",)


class DailyDetailsSerializer(ModelSerializer):
    class Meta:
        model = DailyDetailsRecord
        fields = "__all__"


class LastDayDetailsSerializer(ModelSerializer):
    class Meta:
        model = LastDayDetailsRecord
        exclude = ("id",)
