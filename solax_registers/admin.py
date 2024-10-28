from django.contrib import admin
from django.contrib.sessions.models import Session

from .models import DailyStatsRecord, LastDayStatsRecord, LastMinuteStatsRecord, MinuteStatsRecord

admin.site.site_header = "Solax API"
admin.site.site_url = "/swagger-docs/"
admin.site.register(LastDayStatsRecord)
admin.site.register(LastMinuteStatsRecord)
admin.site.register(MinuteStatsRecord)
admin.site.register(DailyStatsRecord)
admin.site.register(Session)
