# Generated by Django 4.2.6 on 2023-12-01 07:28

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DailyStatsRecord",
            fields=[
                ("upload_date", models.DateField(primary_key=True, serialize=False)),
                (
                    "feed_in_energy_today_meter",
                    models.FloatField(max_length=7, null=True),
                ),
                (
                    "energy_to_grid_today_quantity",
                    models.FloatField(max_length=7, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LastDayStatsRecord",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("upload_date", models.DateField()),
                (
                    "feed_in_energy_today_meter",
                    models.FloatField(max_length=7, null=True),
                ),
                (
                    "energy_to_grid_today_quantity",
                    models.FloatField(max_length=7, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LastMinuteStatsRecord",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("upload_time", models.DateTimeField()),
                ("inverter_status", models.PositiveSmallIntegerField()),
                ("grid_voltage_r", models.PositiveSmallIntegerField(null=True)),
                ("grid_voltage_s", models.PositiveSmallIntegerField(null=True)),
                ("grid_voltage_t", models.PositiveSmallIntegerField(null=True)),
                ("battery_capacity", models.PositiveSmallIntegerField(null=True)),
                ("power_dc1", models.PositiveSmallIntegerField(null=True)),
                ("power_dc2", models.PositiveSmallIntegerField(null=True)),
                ("dc_solar_power", models.PositiveSmallIntegerField(null=True)),
                ("battery_power", models.SmallIntegerField(null=True)),
                ("feed_in_power", models.SmallIntegerField(null=True)),
                ("time_count_down", models.PositiveSmallIntegerField(null=True)),
                ("grid_power", models.SmallIntegerField(null=True)),
                ("energy_from_grid_meter", models.FloatField(max_length=7, null=True)),
                ("energy_to_grid_meter", models.FloatField(max_length=7, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="MinuteStatsRecord",
            fields=[
                (
                    "upload_time",
                    models.DateTimeField(primary_key=True, serialize=False),
                ),
                ("inverter_status", models.PositiveSmallIntegerField()),
                ("grid_voltage_r", models.PositiveSmallIntegerField(null=True)),
                ("grid_voltage_s", models.PositiveSmallIntegerField(null=True)),
                ("grid_voltage_t", models.PositiveSmallIntegerField(null=True)),
                ("battery_capacity", models.PositiveSmallIntegerField(null=True)),
                ("power_dc1", models.PositiveSmallIntegerField(null=True)),
                ("power_dc2", models.PositiveSmallIntegerField(null=True)),
                ("dc_solar_power", models.PositiveSmallIntegerField(null=True)),
                ("battery_power", models.SmallIntegerField(null=True)),
                ("feed_in_power", models.SmallIntegerField(null=True)),
                ("time_count_down", models.PositiveSmallIntegerField(null=True)),
                ("grid_power", models.SmallIntegerField(null=True)),
                ("energy_from_grid_meter", models.FloatField(max_length=7, null=True)),
                ("energy_to_grid_meter", models.FloatField(max_length=7, null=True)),
            ],
        ),
    ]