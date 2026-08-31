"""All the models of this app."""

from django.db import models

from .utils import get_fields_and_pk_name, get_fields_without_pk_flag, read_columns_file

columns_config = read_columns_file()

minute_stats_fields, minute_stats_pk = get_fields_and_pk_name(
    columns_config["minute_stats"]
)
daily_stats_fields, daily_stats_pk = get_fields_and_pk_name(
    columns_config["daily_stats"]
)


class MinuteStatsRecord(models.Model):
    """Represents every-minute inverter data."""

    locals().update(minute_stats_fields)

    def __repr__(self):
        return str(self.pk)


class LastMinuteStatsRecord(models.Model):
    """Represents every-minute inverter data."""

    locals().update(
        get_fields_without_pk_flag(columns_config["minute_stats"], minute_stats_pk)
    )

    def __repr__(self):
        return str(getattr(self, minute_stats_pk))


class DailyStatsRecord(models.Model):
    """Represents daily inverter data."""

    locals().update(daily_stats_fields)

    def __repr__(self):
        return str(self.pk)


class LastDayStatsRecord(models.Model):
    """Represents daily inverter data."""

    locals().update(
        get_fields_without_pk_flag(columns_config["daily_stats"], daily_stats_pk)
    )

    def __repr__(self):
        return str(getattr(self, daily_stats_pk))
