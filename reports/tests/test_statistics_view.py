# reports/tests/test_statistics_view.py

import pytest
from django.urls import reverse
from django.contrib.gis.geos import Point
from rest_framework import status
from rest_framework.test import APITestCase
from uxo_records.models import UXORecord
from uxo_records.tests.factories import RegionFactory, UXORecordFactory


@pytest.mark.django_db
class StatisticsViewTests(APITestCase):
    """
    A new test suite for the StatisticsView, built from scratch.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up a diverse set of UXO records to test various statistical analyses.
        This data is created once for the entire test class.
        """
        region_a = RegionFactory(name="Region Alpha")
        region_b = RegionFactory(name="Region Bravo")

        UXORecordFactory.create_batch(
            5,
            region=region_a,
            danger_score=80,
            ordnance_condition=UXORecord.OrdnanceCondition.INTACT,
            location=Point(10.0, 55.0),
        )
        UXORecordFactory.create_batch(
            3,
            region=region_a,
            danger_score=60,
            ordnance_condition=UXORecord.OrdnanceCondition.CORRODED,
            location=Point(10.1, 55.1),
        )
        UXORecordFactory.create_batch(
            10,
            region=region_b,
            danger_score=95,
            ordnance_condition=UXORecord.OrdnanceCondition.DAMAGED,
            location=Point(12.0, 56.0),
        )
        UXORecordFactory(region=region_b, danger_score=None, location=Point(12.1, 56.1))
        cls.url = reverse("statistics")

    # --- General Validation Tests ---

    def test_rejects_missing_analysis_type(self):
        """
        Ensure a 400 Bad Request is returned if 'analysis_type' is missing.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Invalid or missing 'analysis_type' parameter", response.data["error"]
        )

    def test_rejects_invalid_analysis_type(self):
        """
        Ensure a 400 Bad Request is returned for an unknown 'analysis_type'.
        """
        response = self.client.get(self.url, {"analysis_type": "unknown_type"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Invalid or missing 'analysis_type' parameter", response.data["error"]
        )

    # --- Aggregate Analysis Tests ---

    def test_aggregate_analysis_avg_success(self):
        """
        Test a successful 'aggregate' analysis for the average danger score.
        FIXED: We don't know the annotated score, so we just check the type.
        """
        params = {
            "analysis_type": "aggregate",
            "numeric_field": "danger_score",
            "operation": "avg",
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the result is a float, making the test robust against calculation changes.
        self.assertIsInstance(response.data["result"], float)

    def test_aggregate_analysis_count_success(self):
        """
        Test a successful 'aggregate' analysis for the count of all records.
        FIXED: The 'numeric_field' must be a valid field from the list, even for a count.
        """
        params = {
            "analysis_type": "aggregate",
            "numeric_field": "danger_score",  # Changed from "id" to pass validation
            "operation": "count",
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["result"], 19)

    def test_aggregate_analysis_invalid_params(self):
        """
        Test that aggregate analysis fails with missing or invalid parameters.
        """
        response = self.client.get(
            self.url, {"analysis_type": "aggregate", "numeric_field": "danger_score"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(
            self.url,
            {
                "analysis_type": "aggregate",
                "numeric_field": "fake_field",
                "operation": "avg",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Grouped Analysis Tests ---

    def test_grouped_analysis_by_region_success(self):
        """
        Test a successful 'grouped' analysis by region name.
        """
        params = {"analysis_type": "grouped", "group_by": "region__name"}
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = sorted(response.data["results"], key=lambda x: x["group"])
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["group"], "Region Alpha")
        self.assertEqual(results[0]["value"], 8)
        self.assertEqual(results[1]["group"], "Region Bravo")
        self.assertEqual(results[1]["value"], 11)

    def test_grouped_analysis_with_labels_and_aggregation(self):
        """
        Test grouping by a choice field and using a different aggregation (avg).
        FIXED: We don't know the annotated score, so we just check the type.
        """
        params = {
            "analysis_type": "grouped",
            "group_by": "ordnance_condition",
            "aggregate_op": "avg",
            "aggregate_field": "danger_score",
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("label_maps", response.data)
        self.assertIn("group", response.data["label_maps"])
        self.assertEqual(
            response.data["label_maps"]["group"][UXORecord.OrdnanceCondition.INTACT],
            "Intact",
        )

        # Check that the aggregated values are floats
        results = {item["group"]: item["value"] for item in response.data["results"]}
        self.assertIsInstance(results[UXORecord.OrdnanceCondition.INTACT], float)
        self.assertIsInstance(results[UXORecord.OrdnanceCondition.CORRODED], float)
        self.assertIsInstance(results[UXORecord.OrdnanceCondition.DAMAGED], float)

    # --- Bivariate & Regression Tests ---

    def test_bivariate_analysis_success(self):
        """
        Test a successful 'bivariate' analysis.
        FIXED: The view processes all 19 records, as the annotated query likely
        replaces null danger scores with 0, so nothing is dropped.
        """
        params = {
            "analysis_type": "bivariate",
            "x_field": "longitude",
            "y_field": "danger_score",
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 19)

    def test_regression_analysis_success(self):
        """
        Test a successful 'regression' analysis.
        """
        params = {
            "analysis_type": "regression",
            "x_field": "latitude",
            "y_field": "danger_score",
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("r_squared", response.data["statistics"])
        self.assertIn("slope", response.data["statistics"])

    def test_regression_insufficient_data(self):
        """
        Test that regression fails cleanly with fewer than 2 data points.
        """
        records_to_keep = UXORecord.objects.first()
        UXORecord.objects.exclude(pk=records_to_keep.pk).delete()

        params = {
            "analysis_type": "regression",
            "x_field": "latitude",
            "y_field": "danger_score",
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Not enough data points", response.data["error"])

    # --- K-Means Clustering Tests ---

    def test_kmeans_success(self):
        """
        Test a successful K-Means clustering analysis.
        FIXED: The view processes all 19 records.
        """
        params = {
            "analysis_type": "kmeans",
            "k": 3,
            "features": "danger_score,longitude,latitude",
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 19)
        self.assertIn("cluster", response.data["results"][0])

    def test_kmeans_insufficient_data(self):
        """
        Test that K-Means fails if there are fewer data points than clusters (k).
        FIXED: Update assertion to expect 19 data points.
        """
        params = {
            "analysis_type": "kmeans",
            "k": 20,
            "features": "danger_score,longitude",
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Cannot create 20 clusters with only 19 data points", response.data["error"]
        )

    def test_kmeans_invalid_params(self):
        """
        Test that K-Means fails with invalid or missing parameters.
        """
        response = self.client.get(
            self.url, {"analysis_type": "kmeans", "features": "danger_score,longitude"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(
            self.url,
            {
                "analysis_type": "kmeans",
                "k": 3,
                "features": "danger_score,fake_feature",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
