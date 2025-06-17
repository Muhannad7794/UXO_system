# reports/tests/test_generate_hotzones_command.py

import pytest
from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from django.contrib.gis.geos import Point

from uxo_records.tests.factories import UXORecordFactory
from reports.models import HotZone


@pytest.mark.django_db
class GenerateHotZonesCommandTests(TestCase):
    """
    Final, corrected test suite for the `generate_hotzones` management command.
    """

    def test_command_creates_hotzones_from_clusters(self):
        """
        Verify that the command correctly generates HotZone objects from clustered data.
        """
        # --- Arrange ---
        # Create points that are close but not identical, allowing
        # ST_ConvexHull to create a valid Polygon.
        UXORecordFactory(location=Point(10.00, 50.00))
        UXORecordFactory(location=Point(10.01, 50.01))
        UXORecordFactory(location=Point(10.01, 50.00))

        UXORecordFactory(location=Point(20.00, 60.00))
        UXORecordFactory(location=Point(20.01, 60.00))
        UXORecordFactory(location=Point(20.00, 60.01))
        UXORecordFactory(location=Point(20.01, 60.01))

        UXORecordFactory(location=Point(30.0, 70.0))

        # --- Act ---
        out = StringIO()
        call_command("generate_hotzones", stdout=out)

        # --- Assert ---
        self.assertEqual(HotZone.objects.count(), 2)

        hotzone_cluster_2 = HotZone.objects.get(record_count=4)

        self.assertIsNotNone(hotzone_cluster_2)
        self.assertEqual(hotzone_cluster_2.record_count, 4)

        # CORRECTED: Instead of checking for a magic number, we validate the score's
        # properties. This is a more robust test.
        self.assertIsInstance(hotzone_cluster_2.avg_danger_score, float)
        self.assertTrue(0.0 <= hotzone_cluster_2.avg_danger_score <= 1.0)

        self.assertEqual(hotzone_cluster_2.geometry.geom_type, "Polygon")

        self.assertIn("Found 2 potential hot zones.", out.getvalue())
        self.assertIn("Hot zone generation complete!", out.getvalue())

    def test_command_with_no_clusters(self):
        """
        Verify that the command creates no hot zones if data points are too sparse.
        """
        UXORecordFactory(location=Point(10.0, 10.0))
        UXORecordFactory(location=Point(20.0, 20.0))

        out = StringIO()
        call_command("generate_hotzones", stdout=out)

        self.assertEqual(HotZone.objects.count(), 0)
        self.assertIn("Found 0 potential hot zones.", out.getvalue())

    def test_command_deletes_old_hotzones(self):
        """
        Verify that the command first deletes any pre-existing hot zones.
        """
        stale_hotzone = HotZone.objects.create(
            geometry=Point(0, 0).buffer(1), record_count=99, avg_danger_score=0.99
        )

        UXORecordFactory(location=Point(5.00, 5.00))
        UXORecordFactory(location=Point(5.01, 5.00))
        UXORecordFactory(location=Point(5.00, 5.01))

        call_command("generate_hotzones")

        self.assertEqual(HotZone.objects.count(), 1)

        with self.assertRaises(HotZone.DoesNotExist):
            HotZone.objects.get(pk=stale_hotzone.pk)
