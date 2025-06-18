# reports/tests/test_geospatial_view.py

import pytest
from django.urls import reverse
from django.contrib.gis.geos import Point, Polygon
from rest_framework import status
from rest_framework.test import APITestCase

# Import factories to create test data
from uxo_records.tests.factories import UXORecordFactory
from ..models import HotZone
from .factories import HotZoneFactory


@pytest.mark.django_db
class GeospatialViewTests(APITestCase):
    """
    Final, corrected test suite for the geospatial views.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up geospatial objects for testing.
        """
        cls.record_inside = UXORecordFactory(location=Point(10.0, 55.0))
        cls.record_also_inside = UXORecordFactory(location=Point(10.1, 55.1))
        cls.record_outside = UXORecordFactory(location=Point(12.0, 56.0))
        cls.record_initially_none = UXORecordFactory(
            location=Point(10.2, 55.2), danger_score=None
        )

        HotZone.objects.all().delete()
        cls.hotzone = HotZoneFactory(
            geometry=Polygon.from_bbox((20.0, 60.0, 21.0, 61.0)),
            record_count=25,
            avg_danger_score=0.78,
        )

        cls.heatmap_url = reverse("heatmap")
        cls.bbox_url = reverse("within-bbox")
        cls.hotzone_url = reverse("hotzones")

    def test_heatmap_view_returns_all_records_with_scores(self):
        """
        Ensure the heatmap includes ALL records, as the post_save signal
        ensures every record has a danger score.
        """
        response = self.client.get(self.heatmap_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

        self.record_inside.refresh_from_db()
        expected_point = [
            self.record_inside.location.y,
            self.record_inside.location.x,
            float(self.record_inside.danger_score),
        ]
        self.assertIn(expected_point, response.data)

    def test_records_within_bbox_success(self):
        """
        Ensure the view correctly filters records within a given bounding box.
        """
        bbox_str = "9.9,54.9,10.25,55.25"
        response = self.client.get(self.bbox_url, {"bbox": bbox_str})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        features = response.data.get("features", [])
        self.assertEqual(len(features), 3)

        returned_ids = {item["id"] for item in features}
        self.assertIn(self.record_inside.id, returned_ids)
        self.assertIn(self.record_also_inside.id, returned_ids)
        self.assertIn(self.record_initially_none.id, returned_ids)
        self.assertNotIn(self.record_outside.id, returned_ids)

    def test_records_within_bbox_missing_param(self):
        """
        Test that a 400 error is returned if the 'bbox' parameter is missing.
        """
        response = self.client.get(self.bbox_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("The 'bbox' query parameter is required", response.data["error"])

    def test_records_within_bbox_invalid_param(self):
        """
        Test that a 400 error is returned for various invalid 'bbox' formats.
        """
        response1 = self.client.get(self.bbox_url, {"bbox": "10.0,55.0"})
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("must contain exactly four coordinates", response1.data["error"])

        response2 = self.client.get(self.bbox_url, {"bbox": "a,b,c,d"})
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid 'bbox' format", response2.data["error"])

    def test_hotzone_view_success(self):
        """
        Ensure the view returns a serialized list of all HotZone objects.
        """
        response = self.client.get(self.hotzone_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        features = response.data.get("features", [])
        self.assertEqual(len(features), 1)
        our_hotzone_data = features[0]
        self.assertEqual(our_hotzone_data["id"], self.hotzone.id)
        self.assertEqual(our_hotzone_data["properties"]["record_count"], 25)
        self.assertAlmostEqual(our_hotzone_data["properties"]["avg_danger_score"], 0.78)
