"""All the models of this app."""

from django.db import models

from solax_registers.utils import get_model_field_class

from .utils import read_columns_file

columns_config = read_columns_file()
minute_stats_pk = ""
daily_stats_pk = ""
daily_details_pk = ""


class MinuteStatsRecord(models.Model):
    """Represents every-minute inverter data."""

    for column_info in columns_config["minute_stats"]:
        if column_info.get("primary_key", None) is True:
            globals()["minute_stats_pk"] = column_info["column_name"]

        locals()[column_info["column_name"]] = get_model_field_class(column_info)

    def __repr__(self):
        return str(self.pk)


class LastMinuteStatsRecord(models.Model):
    """Represents every-minute inverter data."""

    for column_info in columns_config["minute_stats"]:
        if column_info["column_name"] == minute_stats_pk:
            del column_info["primary_key"]

        locals()[column_info["column_name"]] = get_model_field_class(column_info)

    def __repr__(self):
        return str(getattr(self, minute_stats_pk))


class DailyStatsRecord(models.Model):
    """Represents daily inverter data."""

    for column_info in columns_config["daily_stats"]:
        if column_info.get("primary_key", None) is True:
            globals()["daily_stats_pk"] = column_info["column_name"]

        locals()[column_info["column_name"]] = get_model_field_class(column_info)

    def __repr__(self):
        return str(self.pk)


class LastDayStatsRecord(models.Model):
    """Represents daily inverter data."""

    for column_info in columns_config["daily_stats"]:
        if column_info["column_name"] == daily_stats_pk:
            del column_info["primary_key"]

        locals()[column_info["column_name"]] = get_model_field_class(column_info)

    def __repr__(self):
        return str(getattr(self, daily_stats_pk))


class DailyDetailsRecord(models.Model):
    """Represents daily inverter data, read minutely."""

    for column_info in columns_config["solax_daily_details"]:
        if column_info.get("primary_key", None) is True:
            globals()["daily_details_pk"] = column_info["column_name"]

        locals()[column_info["column_name"]] = get_model_field_class(column_info)

    def __repr__(self):
        return str(self.pk)


class LastDayDetailsRecord(models.Model):
    """Represents daily inverter data, read minutely."""

    for column_info in columns_config["solax_daily_details"]:
        if column_info["column_name"] == daily_details_pk:
            del column_info["primary_key"]

        locals()[column_info["column_name"]] = get_model_field_class(column_info)

    def __repr__(self):
        return str(getattr(self, daily_details_pk))
