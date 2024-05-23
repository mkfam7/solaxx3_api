from django.urls import reverse_lazy
from rest_framework.test import APITestCase
from .models import MinuteStatsRecord
from rest_framework.status import HTTP_201_CREATED


class Part1MinuteStatsTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.minute_stats = MinuteStatsRecord.objects.create(
            upload_time="2022-07-31 07:56",
            grid_voltage_r=243,
            grid_voltage_s=244,
            grid_voltage_t=242,
            battery_capacity=97,
            power_dc1=55,
            inverter_status=3,
            power_dc2=3788,
            dc_solar_power=5666,
            battery_power=2,
            feed_in_power=2,
            time_count_down=2,
            grid_power=2,
            energy_from_grid_meter=2,
            energy_to_grid_meter=2,
        )

    def test_access_data(self):
        DATA = {"upload_time": "2022-01-01 00:00", "inverter_status": 3}
        RESULT = {
            "upload_time": "2022-07-31 07:56",
            "grid_voltage_r": 243,
            "grid_voltage_s": 244,
            "grid_voltage_t": 242,
            "battery_capacity": 97,
            "power_dc1": 55,
            "inverter_status": 3,
            "power_dc2": 3788,
            "dc_solar_power": 5666,
            "battery_power": 2,
            "feed_in_power": 2,
            "time_count_down": 2,
            "grid_power": 2,
            "energy_from_grid_meter": 2,
            "energy_to_grid_meter": 2,
        }

        URL = reverse_lazy("minute_stats", current_app="solax_registers")

        response = self.client.post(URL, data=DATA, format="json")

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.json(), RESULT)
        self.assertEqual(MinuteStatsRecord.objects.count(), 2)

    def test_number_of_records(self):
        self.assertEqual(MinuteStatsRecord.objects.count(), 1)
