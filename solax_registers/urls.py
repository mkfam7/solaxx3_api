from django.urls import path

from .views import DailyDetails, DailyStats, MinuteStats

urlpatterns = [
    path("minute-stats/", MinuteStats.as_view(), name="minute_stats"),
    path("solax-daily-details/", DailyDetails.as_view(), name="daily_details"),
    path("daily-stats/", DailyStats.as_view(), name="daily_stats"),
]
