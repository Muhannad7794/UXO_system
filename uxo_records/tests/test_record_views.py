# uxo_records/tests/test_record_views.py

import io
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from .factories import UXORecordFactory, RegionFactory
from citizens_reports.tests.factories import UserFactory, AdminUserFactory
from ..models import UXORecord


@pytest.mark.django_db
class TestUXORecordViewSet:
    """
    Test suite for the UXORecordViewSet, covering CRUD operations,
    permissions, filtering, and custom actions.
    """

    def setup_method(self):
        """
        Setup method to create initial data and clients for each test.
        """
        self.user = UserFactory()
        self.admin = AdminUserFactory()

        self.client = APIClient()
        self.user_client = APIClient()
        self.user_client.force_authenticate(user=self.user)
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin)

        self.region = RegionFactory.create()
        UXORecordFactory.create_batch(15, region=self.region)
        self.list_url = reverse("uxorecord-list")

    def test_list_records_permission_denied_for_anonymous(self):
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_records_permission_denied_for_regular_user(self):
        response = self.user_client.get(self.list_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_records_successful_for_admin(self):
        response = self.admin_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.data
        assert "features" in response.data["results"]
        assert len(response.data["results"]["features"]) == 10
        assert response.data["count"] == 15

    def test_retrieve_record_successful_for_admin(self):
        record = UXORecord.objects.first()
        detail_url = reverse("uxorecord-detail", kwargs={"pk": record.pk})
        response = self.admin_client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == record.id
        assert response.data["properties"]["ordnance_type"] == record.ordnance_type

    def test_create_record_successful_for_admin(self):
        record_data = {
            "region": self.region.pk,
            "location": "SRID=4326;POINT (0.2 0.2)",
            "ordnance_type": "IED",
            "ordnance_condition": "LEK",
            "is_loaded": True,
            "proximity_to_civilians": "IMM",
            "burial_status": "EXP",
        }
        response = self.admin_client.post(
            self.list_url, data=record_data, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert UXORecord.objects.count() == 16
        new_record = UXORecord.objects.get(pk=response.data["id"])
        assert new_record.danger_score is not None
        assert new_record.danger_score > 0.9

    def test_all_records_custom_action(self):
        all_records_url = reverse("uxorecord-all-records")
        response = self.admin_client.get(all_records_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["type"] == "FeatureCollection"
        assert len(response.data["features"]) == 15

    def test_filtering_by_ordnance_type(self):
        UXORecordFactory.create(region=self.region, ordnance_type="ART")
        query_url = f"{self.list_url}?ordnance_type=ART"
        response = self.admin_client.get(query_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert (
            response.data["results"]["features"][0]["properties"]["ordnance_type"]
            == "ART"
        )

    def test_filtering_by_danger_score_range(self):
        """
        Verify that filtering by a min/max danger score range works.
        """
        # CORRECTED: Create records with ALL high-risk parameters to guarantee
        # the calculated score will be > 0.9, making the test deterministic.
        UXORecordFactory.create_batch(
            2,
            region=self.region,
            ordnance_type="IED",
            ordnance_condition="LEK",
            is_loaded=True,
            proximity_to_civilians="IMM",
            burial_status="EXP",
        )
        query_url = f"{self.list_url}?danger_score_min=0.9"
        response = self.admin_client.get(query_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_bulk_csv_upload_view(self):
        """
        Integration test for the dedicated bulk CSV upload view.
        """
        csv_content = (
            "latitude,longitude,ordnance_type,ordnance_condition,is_loaded,proximity_to_civilians,burial_status\n"
            "0.5,0.5,Improvised Explosive Device,Leaking/Exuding,True,Immediate (0-100m to civilians/infrastructure),Exposed\n"
            "0.6,0.6,Mortar Bomb,Corroded,False,Near (101-500m),Partially Exposed\n"
        )
        csv_file = io.BytesIO(csv_content.encode("utf-8"))
        csv_file.name = "test_upload.csv"
        upload_url = reverse("uxo-bulk-upload")
        initial_count = UXORecord.objects.count()

        response = self.admin_client.post(
            upload_url, data={"file": csv_file}, format="multipart"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert "Successfully created 2 new UXO records" in response.data["message"]
        assert UXORecord.objects.count() == initial_count + 2
