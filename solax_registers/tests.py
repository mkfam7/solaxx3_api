"""File of API tests."""

from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase

from .models import DailyStatsRecord


class AddHistoryStatsTests(APITestCase):
    """Test POST requests on daily stats model."""

    @classmethod
    def setUpTestData(cls) -> None:
        get_user_model().objects.create(
            username="testuser",
            password="testuser1!",
            is_staff=True,
            is_active=True,
            is_superuser=True,
        )
        cls.testuser = get_user_model().objects.get(username="testuser")

    def test_add_valid_data(self):
        """Test adding a record with valid data."""

        self.client.force_login(self.testuser)

        data = {"upload_date": "2022-01-01"}
        result = {
            "upload_date": "2022-01-01",
            "feed_in_energy_today_meter": None,
            "energy_to_grid_today_quantity": None,
        }
        url = reverse_lazy("daily_stats", current_app="solax_registers")
        response = self.client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertDictEqual(response.json(), result)
        self.assertEqual(DailyStatsRecord.objects.count(), 1)

    def test_with_missing_pk(self):
        """Test posting data with no timestamp."""

        self.client.force_login(self.testuser)

        url = reverse_lazy("daily_stats", current_app="solax_registers")
        response = self.client.post(url, data={}, format="json")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(DailyStatsRecord.objects.count(), 0)

    def test_with_extra_fields(self):
        """Test posting data with extra fields."""

        self.client.force_login(self.testuser)

        data = {"upload_date": "2020-01-01", "extra_field": "extra_value"}
        result = {"Some extra fields were passed:": ["extra_field"]}

        url = reverse_lazy("daily_stats", current_app="solax_registers")
        response = self.client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), result)
        self.assertEqual(DailyStatsRecord.objects.count(), 0)

    def test_with_only_extra_fields(self):
        """Test posting data with only extra fields."""

        self.client.force_login(self.testuser)

        data = {"extra_field": "extra_value"}
        result = {"Some extra fields were passed:": ["extra_field"]}

        url = reverse_lazy("daily_stats", current_app="solax_registers")
        response = self.client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), result)
        self.assertEqual(DailyStatsRecord.objects.count(), 0)

    def test_force_parameter_true(self):
        """Test posting data, passing `force=true`."""

        self.client.force_login(self.testuser)

        data = {"upload_date": "2020-01-01"}

        url = reverse_lazy("daily_stats", current_app="solax_registers")
        self.client.post(url, data=data, format="json")
        response = self.client.post(
            url, data=data, format="json", QUERY_STRING="force=true"
        )

        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_force_parameter_false(self):
        """Test posting data, passing `force=false`."""

        self.client.force_login(self.testuser)

        data = {"upload_date": "2020-01-01"}

        url = reverse_lazy("daily_stats", current_app="solax_registers")
        self.client.post(url, data=data, format="json")
        response = self.client.post(
            url, data=data, format="json", QUERY_STRING="force=false"
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(DailyStatsRecord.objects.count(), 1)

    def test_no_force_parameter(self):
        """Test posting data without passing `force` parameter."""

        self.client.force_login(self.testuser)

        data = {"upload_date": "2020-01-01"}

        url = reverse_lazy("daily_stats", current_app="solax_registers")
        self.client.post(url, data=data, format="json")
        response = self.client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(DailyStatsRecord.objects.count(), 1)
