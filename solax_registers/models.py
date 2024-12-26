"""All the models of this app."""

import json
from os import environ

from django.db import models

from solax_registers.utils import parse_column_info
from .utils import read_columns_file

columns_config = read_columns_file()


class MinuteStatsRecord(models.Model):
    """Represents every-minute inverter data."""

    upload_time = models.DateTimeField(primary_key=True)

    for column_info in columns_config["minute_stats"]:
        locals()[column_info["column_name"]] = parse_column_info(column_info)

    def __repr__(self):
        return str(self.upload_time)


class LastMinuteStatsRecord(models.Model):
    """Represents every-minute inverter data."""

    upload_time = models.DateTimeField()

    for column_info in columns_config["minute_stats"]:
        locals()[column_info["column_name"]] = parse_column_info(column_info)

    def __repr__(self):
        return str(self.upload_time)


class DailyStatsRecord(models.Model):
    """Represents daily inverter data."""

    upload_date = models.DateField(primary_key=True)

    for column_info in columns_config["daily_stats"]:
        locals()[column_info["column_name"]] = parse_column_info(column_info)

    def __repr__(self):
        return str(self.upload_date)


class LastDayStatsRecord(models.Model):
    """Represents daily inverter data."""

    upload_date = models.DateField()

    for column_info in columns_config["daily_stats"]:
        locals()[column_info["column_name"]] = parse_column_info(column_info)

    def __repr__(self):
        return str(self.upload_date)
