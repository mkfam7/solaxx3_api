from django.contrib import admin
from django.contrib.sessions.models import Session

from .models import *

admin.site.register(LastDayStatsRecord)
admin.site.register(LastMinuteStatsRecord)
admin.site.register(MinuteStatsRecord)
admin.site.register(DailyStatsRecord)
admin.site.register(Session)
