from django.urls import path

from .views import (
    GetUpdateLastDayStats,
    GetUpdateLastMinuteStats,
    ListAddDailyStats,
    ListAddMinuteStats,
)

urlpatterns = [
    path("minute-stats/", ListAddMinuteStats.as_view(), name="minute_stats"),
    path(
        "last-minute-stats/",
        GetUpdateLastMinuteStats.as_view(),
        name="last_minute_stats",
    ),
    path("daily-stats/", ListAddDailyStats.as_view(), name="daily_stats"),
    path(
        "last-day-stats/",
        GetUpdateLastDayStats.as_view(),
        name="last_day_stats",
    ),
]
