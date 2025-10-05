from django.urls import path

from .views import DailyStats

urlpatterns = [
    path("daily-stats/", DailyStats.as_view(), name="daily_stats"),
    # path("daily-stats/", ListAddDailyStats.as_view(), name="daily_stats"),
]
