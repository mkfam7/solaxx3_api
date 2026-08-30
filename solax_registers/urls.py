from django.urls import path

from .views import DailyStats, MinuteStats

urlpatterns = [
    path("minute-stats/", MinuteStats.as_view(), name="minute_stats"),
    path("daily-stats/", DailyStats.as_view(), name="daily_stats"),
]
