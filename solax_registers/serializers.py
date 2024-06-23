from rest_framework.serializers import ModelSerializer

from .models import (
    DailyStatsRecord,
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
        fields = "__all__"


class LastDayStatsSerializer(ModelSerializer):
    class Meta:
        model = LastDayStatsRecord
        fields = "__all__"
