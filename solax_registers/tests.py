"""File of API tests."""

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse_lazy
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase

from .constants import error
from .models import DailyStatsRecord, LastDayStatsRecord

User = get_user_model()


@override_settings(SECRET_KEY="django-insecure-o$ax$#*gng6qi*j#&9lwof070#f=v^7e9ck)_70@t60kppj&hz")
class AddHistoryStatsTests(APITestCase):
    """Tests for adding history stats."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data."""
        User.objects.create(
            username="testuser",
            password="testuser1!",
            is_staff=True,
            is_active=True,
            is_superuser=True,
        )
        cls.testuser = User.objects.get(username="testuser")

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

        url = reverse_lazy("daily_stats", current_app="solax_registers")
        response = self.client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(DailyStatsRecord.objects.count(), 0)

        self.assertIn("Some extra fields were passed:", response.json())
        extra_fields = response.json()["Some extra fields were passed:"]
        self.assertListEqual(sorted(extra_fields), ["extra_field"])

    def test_with_only_extra_fields(self):
        """Test posting data with only extra fields."""

        self.client.force_login(self.testuser)

        data = {"extra_field": "extra_value"}

        url = reverse_lazy("daily_stats", current_app="solax_registers")
        response = self.client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(DailyStatsRecord.objects.count(), 0)

        self.assertIn("Some extra fields were passed:", response.json())
        extra_fields = response.json()["Some extra fields were passed:"]
        self.assertListEqual(sorted(extra_fields), ["extra_field"])

    def test_force_parameter_true(self):
        """Test posting data, passing `overwrite=true`."""

        self.client.force_login(self.testuser)

        data = {"upload_date": "2020-01-01"}

        url = reverse_lazy("daily_stats", current_app="solax_registers")
        self.client.post(url, data=data, format="json")
        response = self.client.post(url, data=data, format="json", QUERY_STRING="overwrite=true")

        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_force_parameter_false(self):
        """Test posting data, passing `overwrite=false`."""

        self.client.force_login(self.testuser)

        data = {"upload_date": "2020-01-01"}

        url = reverse_lazy("daily_stats", current_app="solax_registers")
        self.client.post(url, data=data, format="json")
        response = self.client.post(url, data=data, format="json", QUERY_STRING="overwrite=false")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(DailyStatsRecord.objects.count(), 1)

    def test_no_force_parameter(self):
        """Test posting data without passing `overwrite` parameter."""

        self.client.force_login(self.testuser)

        data = {"upload_date": "2020-01-01"}

        url = reverse_lazy("daily_stats", current_app="solax_registers")
        self.client.post(url, data=data, format="json")
        response = self.client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(DailyStatsRecord.objects.count(), 1)

    def test_invalid_force_parameter(self):
        """Test posting data with an invalid `overwrite` parameter."""

        self.client.force_login(self.testuser)
        data = {"upload_date": "2020-01-01"}

        url = reverse_lazy("daily_stats", current_app="solax_registers")
        response = self.client.post(url, data=data, format="json", QUERY_STRING="overwrite=x")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), error.INVALID_FORCE_PARAM.data)
        self.assertEqual(DailyStatsRecord.objects.count(), 0)


@override_settings(SECRET_KEY="django-insecure-o$ax$#*gng6qi*j#&9lwof070#f=v^7e9ck)_70@t60kppj&hz")
class GetHistoryStatsTests(APITestCase):
    """Tests for getting history stats."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data."""

        User.objects.create(
            username="testuser",
            password="testuser1!",
            is_staff=True,
            is_active=True,
            is_superuser=True,
        )
        cls.testuser = User.objects.get(username="testuser")

        DailyStatsRecord(upload_date="2020-01-01").save()
        DailyStatsRecord(upload_date="2021-01-01").save()
        DailyStatsRecord(upload_date="2022-01-01").save()

    def test_with_no_stats_parameter(self):
        """Try to get data without specifying the `fields` parameter."""

        self.client.force_login(self.testuser)
        response = self.client.get(reverse_lazy("daily_stats"), data={}, QUERY_STRING="")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), error.MISSING_FIELDS.data)

    def test_get_all_data(self):
        """Try to get all data."""

        self.client.force_login(self.testuser)

        result = [
            {
                "upload_date": "2020-01-01",
                "feed_in_energy_today_meter": None,
                "energy_to_grid_today_quantity": None,
            },
            {
                "upload_date": "2021-01-01",
                "feed_in_energy_today_meter": None,
                "energy_to_grid_today_quantity": None,
            },
            {
                "upload_date": "2022-01-01",
                "feed_in_energy_today_meter": None,
                "energy_to_grid_today_quantity": None,
            },
        ]

        response = self.client.get(reverse_lazy("daily_stats"), data={}, QUERY_STRING="fields=all")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertListEqual(response.json(), result)

    def test_with_extra_stats(self):
        """Try to get data by adding fake field names to the `stats` parameter."""

        self.client.force_login(self.testuser)

        response = self.client.get(
            reverse_lazy("daily_stats"),
            data={},
            QUERY_STRING="fields=all&fields=extra",
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        self.assertIn("Some extra fields were passed:", response.json())
        extra_fields = response.json()["Some extra fields were passed:"]
        self.assertListEqual(sorted(extra_fields), ["all", "extra"])

    def test_with_only_extra_stats(self):
        """Try to get data by adding only fake field names to the `fields` parameter."""

        self.client.force_login(self.testuser)

        response = self.client.get(
            reverse_lazy("daily_stats"),
            data={},
            QUERY_STRING="fields=extra1&fields=extra2",
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        self.assertIn("Some extra fields were passed:", response.json())
        extra_fields = response.json()["Some extra fields were passed:"]
        self.assertListEqual(sorted(extra_fields), ["extra1", "extra2"])

    def test_before_parameter(self):
        """Try to filter data using the `before` parameter."""

        self.client.force_login(self.testuser)

        result = [{"upload_date": "2020-01-01"}, {"upload_date": "2021-01-01"}]

        response = self.client.get(
            reverse_lazy("daily_stats"),
            data={},
            QUERY_STRING="fields=upload_date&before=2021-01-01",
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertListEqual(response.json(), result)

    def test_after_parameter(self):
        """Try to filter data using the `after` parameter."""

        self.client.force_login(self.testuser)

        result = [{"upload_date": "2021-01-01"}, {"upload_date": "2022-01-01"}]

        response = self.client.get(
            reverse_lazy("daily_stats"),
            data={},
            QUERY_STRING="fields=upload_date&since=2021-01-01",
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertListEqual(response.json(), result)

    def test_before_after_parameters(self):
        """Try to filter data using the `after` and `before` parameters combined."""

        self.client.force_login(self.testuser)

        result = [{"upload_date": "2021-01-01"}]

        response = self.client.get(
            reverse_lazy("daily_stats"),
            data={},
            QUERY_STRING="fields=upload_date&since=2021-01-01&before=2021-01-01",
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertListEqual(response.json(), result)


@override_settings(SECRET_KEY="django-insecure-o$ax$#*gng6qi*j#&9lwof070#f=v^7e9ck)_70@t60kppj&hz")
class DeleteHistoryStatsTests(APITestCase):
    """Tests to test deleting history tests."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data."""

        User.objects.create(
            username="testuser",
            password="testuser1!",
            is_staff=True,
            is_active=True,
            is_superuser=True,
        )
        cls.testuser = User.objects.get(username="testuser")

        DailyStatsRecord(upload_date="2020-01-01").save()
        DailyStatsRecord(upload_date="2021-01-01").save()
        DailyStatsRecord(upload_date="2022-01-01").save()

    def test_deleting_with_no_action(self):
        """Try to delete data without passing the `action` parameter."""

        self.client.force_login(user=self.testuser)

        response = self.client.delete(reverse_lazy("daily_stats"))
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), error.MISSING_ACTION_PARAM.data)

    def test_deleting_with_nonexistent_action(self):
        """Try to delete data with passing an invalid `action` parameter."""

        self.client.force_login(user=self.testuser)

        response = self.client.delete(reverse_lazy("daily_stats"), QUERY_STRING="action=x")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), error.INVALID_ACTION_PARAM.data)

    def test_truncate(self):
        """Try to delete all data."""

        self.client.force_login(user=self.testuser)
        result = {"deleted": 3}

        response = self.client.delete(reverse_lazy("daily_stats"), QUERY_STRING="action=truncate")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.json(), result)

    def test_delete_older_than_date(self):
        """Try to delete all data older than a given date."""

        self.client.force_login(user=self.testuser)
        result = {"deleted": 2}

        response = self.client.delete(
            reverse_lazy("daily_stats"),
            QUERY_STRING="action=delete_older_than&args=2021-01-01",
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.json(), result)

    def test_delete_older_than_without_date(self):
        """Try to delete all data older than x date, but not pass any date."""

        self.client.force_login(user=self.testuser)

        response = self.client.delete(
            reverse_lazy("daily_stats"),
            QUERY_STRING="action=delete_older_than",
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), error.MISSING_DATE_ARG.data)


@override_settings(SECRET_KEY="django-insecure-o$ax$#*gng6qi*j#&9lwof070#f=v^7e9ck)_70@t60kppj&hz")
class AddLastHistoryStatsTests(APITestCase):
    """Tests for adding last history stats."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data."""
        User.objects.create(
            username="testuser",
            password="testuser1!",
            is_staff=True,
            is_active=True,
            is_superuser=True,
        )
        cls.testuser = User.objects.get(username="testuser")
        LastDayStatsRecord(upload_date="2019-01-01").save()

    def test_add_valid_data(self):
        """Test adding a record with valid data."""

        self.client.force_login(self.testuser)

        data = {"upload_date": "2022-01-01"}
        result = {
            "id": 2,
            "upload_date": "2022-01-01",
            "feed_in_energy_today_meter": None,
            "energy_to_grid_today_quantity": None,
        }
        url = reverse_lazy("last_day_stats", current_app="solax_registers")
        response = self.client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertDictEqual(response.json(), result)
        self.assertEqual(LastDayStatsRecord.objects.count(), 1)

    def test_with_missing_pk(self):
        """Test posting data with no timestamp."""

        self.client.force_login(self.testuser)

        url = reverse_lazy("last_day_stats", current_app="solax_registers")
        response = self.client.post(url, data={}, format="json")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(LastDayStatsRecord.objects.count(), 0)

    def test_with_extra_fields(self):
        """Test posting data with extra fields."""

        self.client.force_login(self.testuser)

        data = {"upload_date": "2020-01-01", "extra_field": "extra_value"}

        url = reverse_lazy("last_day_stats", current_app="solax_registers")
        response = self.client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(LastDayStatsRecord.objects.count(), 1)

        self.assertIn("Some extra fields were passed:", response.json())
        extra_fields = response.json()["Some extra fields were passed:"]
        self.assertListEqual(sorted(extra_fields), ["extra_field"])

    def test_with_only_extra_fields(self):
        """Test posting data with only extra fields."""

        self.client.force_login(self.testuser)

        data = {"extra_field": "extra_value"}

        url = reverse_lazy("last_day_stats", current_app="solax_registers")
        response = self.client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(LastDayStatsRecord.objects.count(), 1)

        self.assertIn("Some extra fields were passed:", response.json())
        extra_fields = response.json()["Some extra fields were passed:"]
        self.assertListEqual(sorted(extra_fields), ["extra_field"])


@override_settings(SECRET_KEY="django-insecure-o$ax$#*gng6qi*j#&9lwof070#f=v^7e9ck)_70@t60kppj&hz")
class GetLastHistoryStatsTests(APITestCase):
    """Tests for getting last history stats."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data."""

        User.objects.create(
            username="testuser",
            password="testuser1!",
            is_staff=True,
            is_active=True,
            is_superuser=True,
        )
        cls.testuser = User.objects.get(username="testuser")
        LastDayStatsRecord(upload_date="2020-01-01").save()

    def test_with_no_stats_parameter(self):
        """Try to get data without specifying the `fields` parameter."""

        self.client.force_login(self.testuser)
        response = self.client.get(reverse_lazy("last_day_stats"), data={})

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), error.MISSING_FIELDS.data)

    def test_get_all_data(self):
        """Try to get all data."""

        self.client.force_login(self.testuser)

        result = {
            "id": 1,
            "upload_date": "2020-01-01",
            "feed_in_energy_today_meter": None,
            "energy_to_grid_today_quantity": None,
        }

        response = self.client.get(
            reverse_lazy("last_day_stats"),
            data={},
            QUERY_STRING="fields=all",
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertDictEqual(response.json(), result)

    def test_with_extra_stats(self):
        """Try to get data by adding fake field names to the `fields` parameter."""

        self.client.force_login(self.testuser)

        response = self.client.get(
            reverse_lazy("last_day_stats"),
            data={},
            QUERY_STRING="fields=all&fields=extra",
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        self.assertIn("Some extra fields were passed:", response.json())
        extra_fields = response.json()["Some extra fields were passed:"]
        self.assertListEqual(sorted(extra_fields), ["all", "extra"])

    def test_with_only_extra_stats(self):
        """Try to get data by adding only fake field names to the `fields` parameter."""

        self.client.force_login(self.testuser)

        response = self.client.get(
            reverse_lazy("last_day_stats"),
            data={},
            QUERY_STRING="fields=extra1&fields=extra2",
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        self.assertIn("Some extra fields were passed:", response.json())
        extra_fields = response.json()["Some extra fields were passed:"]
        self.assertListEqual(sorted(extra_fields), ["extra1", "extra2"])


class TestHealthz(APITestCase):
    "Tests for the healthz endpoint"

    def test_healthz(self):
        response = self.client.get(reverse_lazy("healthz"))
        self.assertEqual(response.json(), "healthy")
        self.assertEqual(response.status_code, 200)
