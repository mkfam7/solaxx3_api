"""All the models of this app."""

import json
from os import environ

from django.db import models

from solax_registers.utils import parse_column_info

columns_file = environ.get("COLUMNS_FILE", "columns.json")


class MinuteStatsRecord(models.Model):
    """Represents every-minute inverter data."""

    upload_time = models.DateTimeField(primary_key=True)

    with open(columns_file, encoding="utf-8") as f:
        columns = json.load(f)["minute_stats"]

    for column_info in columns:
        locals()[column_info["column_name"]] = parse_column_info(column_info)

    def __repr__(self):
        return str(self.upload_time)


class LastMinuteStatsRecord(models.Model):
    """Represents every-minute inverter data."""

    upload_time = models.DateTimeField()

    with open(columns_file, encoding="utf-8") as f:
        columns = json.load(f)["minute_stats"]

    for column_info in columns:
        locals()[column_info["column_name"]] = parse_column_info(column_info)

    def __repr__(self):
        return str(self.upload_time)


class DailyStatsRecord(models.Model):
    """Represents daily inverter data."""

    upload_date = models.DateField(primary_key=True)

    with open(columns_file, encoding="utf-8") as f:
        columns = json.load(f)["daily_stats"]

    for column_info in columns:
        locals()[column_info["column_name"]] = parse_column_info(column_info)

    def __repr__(self):
        return str(self.upload_date)


class LastDayStatsRecord(models.Model):
    """Represents daily inverter data."""

    upload_date = models.DateField()

    with open(columns_file, encoding="utf-8") as f:
        columns = json.load(f)["daily_stats"]

    for column_info in columns:
        locals()[column_info["column_name"]] = parse_column_info(column_info)

    def __repr__(self):
        return str(self.upload_date)
