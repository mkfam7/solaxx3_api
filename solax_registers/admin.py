from django.contrib import admin

from .models import *
from django.contrib.sessions.models import Session


admin.site.register(LastDayStatsRecord)
admin.site.register(LastMinuteStatsRecord)
admin.site.register(MinuteStatsRecord)
admin.site.register(DailyStatsRecord)
admin.site.register(Session)
