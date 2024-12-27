"""File of API tests."""

import unittest

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse_lazy
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase

from .constants import error
from .models import DailyStatsRecord, LastDayStatsRecord
from .utils import get_a_nonexistent_column, get_sample_column_values, parse_column_info, read_columns_file

User = get_user_model()
columns = read_columns_file()


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
        result = get_sample_column_values(
            columns["daily_stats"],
            {"positive_small_integer": None, "small_integer": None, "integer": None, "float": None},
            {"upload_date": "2022-01-01"},
            datetime_pk=False,
        )
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

        nonexistent_column = get_a_nonexistent_column()

        data = {"upload_date": "2020-01-01", nonexistent_column: "extra_value"}

        url = reverse_lazy("daily_stats", current_app="solax_registers")
        response = self.client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(DailyStatsRecord.objects.count(), 0)

        self.assertIn("Some extra fields were passed:", response.json())
        extra_fields = response.json()["Some extra fields were passed:"]
        self.assertListEqual(sorted(extra_fields), [nonexistent_column])

    def _get_a_nonexistent_column(self):
        columns_for_daily_stats = columns["daily_stats"]
        if columns_for_daily_stats:
            nonexistent_column = columns_for_daily_stats[0]["column_name"] + "x"
        else:
            nonexistent_column = "extra"
        return nonexistent_column

    def test_with_only_extra_fields(self):
        """Test posting data with only extra fields."""

        self.client.force_login(self.testuser)

        extra_column = get_a_nonexistent_column()
        data = {extra_column: "extra_value"}

        url = reverse_lazy("daily_stats", current_app="solax_registers")
        response = self.client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(DailyStatsRecord.objects.count(), 0)

        self.assertIn("Some extra fields were passed:", response.json())
        extra_fields = response.json()["Some extra fields were passed:"]
        self.assertListEqual(sorted(extra_fields), [extra_column])

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

        DailyStatsRecord.objects.bulk_create(
            [
                DailyStatsRecord(upload_date="2020-01-01"),
                DailyStatsRecord(upload_date="2021-01-01"),
                DailyStatsRecord(upload_date="2022-01-01"),
            ],
        )

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
            get_sample_column_values(
                columns["daily_stats"],
                {"positive_small_integer": None, "small_integer": None, "integer": None, "float": None},
                {"upload_date": "2020-01-01"},
                datetime_pk=False,
            ),
            get_sample_column_values(
                columns["daily_stats"],
                {"positive_small_integer": None, "small_integer": None, "integer": None, "float": None},
                {"upload_date": "2021-01-01"},
                datetime_pk=False,
            ),
            get_sample_column_values(
                columns["daily_stats"],
                {"positive_small_integer": None, "small_integer": None, "integer": None, "float": None},
                {"upload_date": "2022-01-01"},
                datetime_pk=False,
            ),
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
        first_extra_field = get_a_nonexistent_column(0)
        second_extra_field = get_a_nonexistent_column(1)

        response = self.client.get(
            reverse_lazy("daily_stats"),
            data={},
            QUERY_STRING=f"fields={first_extra_field}&fields={second_extra_field}",
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        self.assertIn("Some extra fields were passed:", response.json())
        extra_fields = response.json()["Some extra fields were passed:"]
        self.assertListEqual(sorted(extra_fields), [first_extra_field, second_extra_field])

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

        DailyStatsRecord.objects.bulk_create(
            [
                DailyStatsRecord(upload_date="2020-01-01"),
                DailyStatsRecord(upload_date="2021-01-01"),
                DailyStatsRecord(upload_date="2022-01-01"),
            ]
        )

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
        result = get_sample_column_values(
            columns["daily_stats"],
            {"positive_small_integer": None, "small_integer": None, "integer": None, "float": None},
            {"upload_date": "2022-01-01"},
            datetime_pk=False,
        )
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

        extra_field = get_a_nonexistent_column()
        data = {"upload_date": "2020-01-01", extra_field: "extra_value"}

        url = reverse_lazy("last_day_stats", current_app="solax_registers")
        response = self.client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(LastDayStatsRecord.objects.count(), 1)

        self.assertIn("Some extra fields were passed:", response.json())
        extra_fields = response.json()["Some extra fields were passed:"]
        self.assertListEqual(sorted(extra_fields), [extra_field])

    def test_with_only_extra_fields(self):
        """Test posting data with only extra fields."""

        self.client.force_login(self.testuser)

        extra_field = get_a_nonexistent_column()
        data = {extra_field: "extra_value"}

        url = reverse_lazy("last_day_stats", current_app="solax_registers")
        response = self.client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(LastDayStatsRecord.objects.count(), 1)

        self.assertIn("Some extra fields were passed:", response.json())
        extra_fields = response.json()["Some extra fields were passed:"]
        self.assertListEqual(sorted(extra_fields), [extra_field])


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

        result = get_sample_column_values(
            columns["daily_stats"],
            {"positive_small_integer": None, "small_integer": None, "integer": None, "float": None},
            {"upload_date": "2020-01-01"},
            datetime_pk=False,
        )

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

        extra_field = get_a_nonexistent_column()
        response = self.client.get(
            reverse_lazy("last_day_stats"),
            data={},
            QUERY_STRING=f"fields=all&fields={extra_field}",
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        self.assertIn("Some extra fields were passed:", response.json())
        extra_fields = response.json()["Some extra fields were passed:"]
        self.assertListEqual(sorted(extra_fields), ["all", extra_field])

    def test_with_only_extra_stats(self):
        """Try to get data by adding only fake field names to the `fields` parameter."""

        self.client.force_login(self.testuser)

        extra_field1 = get_a_nonexistent_column(0)
        extra_field2 = get_a_nonexistent_column(1)
        response = self.client.get(
            reverse_lazy("last_day_stats"),
            data={},
            QUERY_STRING=f"fields={extra_field1}&fields={extra_field2}",
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        self.assertIn("Some extra fields were passed:", response.json())
        extra_fields = response.json()["Some extra fields were passed:"]
        self.assertListEqual(sorted(extra_fields), [extra_field1, extra_field2])


class TestHealthz(APITestCase):
    "Tests for the healthz endpoint"

    def test_healthz(self):
        response = self.client.get(reverse_lazy("healthz"))
        self.assertEqual(response.json(), "healthy")
        self.assertEqual(response.status_code, 200)


class TestParseColumnInfo(unittest.TestCase):
    @unittest.expectedFailure
    def test_parse_with_invalid_type(self):
        "Try parsing column info with an invalid type."

        parse_column_info(
            {
                "column_name": "inverter_status",
                "column_type": "sample",
                "nullable": "N/A",
                "default": 0,
                "length": "N/A",
            }
        )

    def test_parse_with_valid_type(self):
        "Try parsing column info with a valid type."

        parse_column_info(
            {
                "column_name": "inverter_status",
                "column_type": "integer",
                "nullable": "N/A",
                "default": 0,
                "length": "N/A",
            }
        )

    @unittest.expectedFailure
    def test_parse_with_invalid_nullable(self):
        "Try parsing column info with an invalid nullable field."

        parse_column_info(
            {
                "column_name": "inverter_status",
                "column_type": "integer",
                "nullable": "invalid",
                "default": 0,
                "length": "N/A",
            }
        )

    def test_parse_with_valid_nullable(self):
        "Try parsing column info with a valid nullable field."

        parse_column_info(
            {
                "column_name": "inverter_status",
                "column_type": "integer",
                "nullable": True,
                "default": 0,
                "length": "N/A",
            }
        )

    def test_parse_with_na_nullable(self):
        "Try parsing column info with an 'N/A' value for the nullable field."

        parse_column_info(
            {
                "column_name": "inverter_status",
                "column_type": "integer",
                "nullable": "N/A",
                "default": 0,
                "length": "N/A",
            }
        )

    @unittest.expectedFailure
    def test_parse_with_string_length(self):
        "Try parsing column info with an invalid column length."

        parse_column_info(
            {
                "column_name": "inverter_status",
                "column_type": "integer",
                "nullable": "N/A",
                "default": 0,
                "length": "string",
            }
        )

    def test_parse_with_na_length(self):
        "Try parsing column info with an empty value for length."

        parse_column_info(
            {
                "column_name": "inverter_status",
                "column_type": "integer",
                "nullable": "N/A",
                "default": 0,
                "length": "N/A",
            }
        )

    @unittest.expectedFailure
    def test_parse_with_neg_length(self):
        "Try parsing column info with a negative length."

        parse_column_info(
            {
                "column_name": "inverter_status",
                "column_type": "integer",
                "nullable": "N/A",
                "default": 0,
                "length": -1,
            }
        )

    @unittest.expectedFailure
    def test_parse_with_0_length(self):
        "Try parsing column info with length=0."

        parse_column_info(
            {
                "column_name": "inverter_status",
                "column_type": "integer",
                "nullable": "N/A",
                "default": 0,
                "length": 0,
            }
        )

    def test_parse_with_positive_length(self):
        "Try parsing column info with a valid length."

        parse_column_info(
            {
                "column_name": "inverter_status",
                "column_type": "integer",
                "nullable": "N/A",
                "default": 0,
                "length": 1,
            }
        )
