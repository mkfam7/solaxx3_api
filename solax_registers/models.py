from django.db import models


class MinuteStatsRecord(models.Model):
    upload_time = models.DateTimeField(primary_key=True)
    inverter_status = models.PositiveSmallIntegerField(default=0)
    grid_voltage_r = models.PositiveSmallIntegerField(null=True)
    grid_voltage_s = models.PositiveSmallIntegerField(null=True)
    grid_voltage_t = models.PositiveSmallIntegerField(null=True)
    battery_capacity = models.PositiveSmallIntegerField(null=True)
    power_dc1 = models.PositiveSmallIntegerField(null=True)
    power_dc2 = models.PositiveSmallIntegerField(null=True)
    dc_solar_power = models.PositiveSmallIntegerField(null=True)
    battery_power = models.SmallIntegerField(null=True)
    feed_in_power = models.SmallIntegerField(null=True)
    time_count_down = models.PositiveSmallIntegerField(null=True)
    grid_power = models.SmallIntegerField(null=True)
    energy_from_grid_meter = models.FloatField(max_length=7, null=True)
    energy_to_grid_meter = models.FloatField(max_length=7, null=True)
    inv_volt_r = models.SmallIntegerField(null=True)
    inv_volt_s = models.SmallIntegerField(null=True)
    inv_volt_t = models.SmallIntegerField(null=True)
    off_grid_power_active_r = models.IntegerField(null=True)
    off_grid_power_active_s = models.IntegerField(null=True)
    off_grid_power_active_t = models.IntegerField(null=True)
    grid_power_r = models.IntegerField(null=True)
    grid_power_s = models.IntegerField(null=True)
    grid_power_t = models.IntegerField(null=True)

    def __repr__(self):
        return str(self.upload_time)


class LastMinuteStatsRecord(models.Model):
    upload_time = models.DateTimeField()
    inverter_status = models.PositiveSmallIntegerField(default=0)
    grid_voltage_r = models.PositiveSmallIntegerField(null=True)
    grid_voltage_s = models.PositiveSmallIntegerField(null=True)
    grid_voltage_t = models.PositiveSmallIntegerField(null=True)
    battery_capacity = models.PositiveSmallIntegerField(null=True)
    power_dc1 = models.PositiveSmallIntegerField(null=True)
    power_dc2 = models.PositiveSmallIntegerField(null=True)
    dc_solar_power = models.PositiveSmallIntegerField(null=True)
    battery_power = models.SmallIntegerField(null=True)
    feed_in_power = models.SmallIntegerField(null=True)
    time_count_down = models.PositiveSmallIntegerField(null=True)
    grid_power = models.SmallIntegerField(null=True)
    energy_from_grid_meter = models.FloatField(max_length=7, null=True)
    energy_to_grid_meter = models.FloatField(max_length=7, null=True)
    inv_volt_r = models.SmallIntegerField(null=True)
    inv_volt_s = models.SmallIntegerField(null=True)
    inv_volt_t = models.SmallIntegerField(null=True)
    off_grid_power_active_r = models.IntegerField(null=True)
    off_grid_power_active_s = models.IntegerField(null=True)
    off_grid_power_active_t = models.IntegerField(null=True)
    grid_power_r = models.IntegerField(null=True)
    grid_power_s = models.IntegerField(null=True)
    grid_power_t = models.IntegerField(null=True)

    def __repr__(self):
        return str(self.upload_time)


class DailyStatsRecord(models.Model):
    upload_date = models.DateField(primary_key=True)
    feed_in_energy_today_meter = models.FloatField(max_length=7, null=True)
    energy_to_grid_today_quantity = models.FloatField(max_length=7, null=True)

    def __repr__(self):
        return str(self.upload_date)


class LastDayStatsRecord(models.Model):
    upload_date = models.DateField()
    feed_in_energy_today_meter = models.FloatField(max_length=7, null=True)
    energy_to_grid_today_quantity = models.FloatField(max_length=7, null=True)

    def __repr__(self):
        return str(self.upload_date)
