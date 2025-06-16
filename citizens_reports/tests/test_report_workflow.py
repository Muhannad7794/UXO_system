# citizens_reports/tests/test_report_workflow.py

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from ..models import CitizenReport
from uxo_records.models import UXORecord

from .factories import AdminUserFactory, CitizenReportFactory
from uxo_records.tests.factories import RegionFactory


@pytest.mark.django_db
class TestCitizenReportWorkflow:
    """
    A test suite for the entire citizen report workflow, from submission to verification.
    """

    def test_anonymous_user_can_submit_report(self):
        """
        Tests that an unauthenticated user can successfully submit a new report.
        """
        client = APIClient()
        image_file = CitizenReportFactory.build().image
        report_data = {
            "name": "John",
            "last_name": "Doe",
            "phone_number": "555-1234",
            "national_nr": "1234567890",
            "description": "Found a rusty shell near the old bridge.",
            "image": image_file,
            "location": "SRID=4326;POINT (0.5 0.5)",
        }
        submit_url = reverse("submit-citizen-report")

        response = client.post(submit_url, data=report_data, format="multipart")

        assert response.status_code == status.HTTP_201_CREATED
        assert CitizenReport.objects.count() == 1
        assert CitizenReport.objects.first().status == "pending"

    def test_non_admin_user_cannot_view_review_list(self):
        """
        Tests that a regular, authenticated but non-admin user is denied access
        to the review list.
        """
        client = APIClient()
        user = AdminUserFactory(is_staff=False, is_superuser=False)
        client.force_authenticate(user=user)
        review_url = reverse("list-citizen-reports")

        response = client.get(review_url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_verify_report_and_create_uxo_record(self):
        """
        Tests the complete verification pipeline.
        """
        RegionFactory.create()
        citizen_report = CitizenReportFactory.create()
        client = APIClient()
        admin_user = AdminUserFactory()
        client.force_authenticate(user=admin_user)
        verify_url = reverse("verify-citizen-report", kwargs={"pk": citizen_report.pk})
        verification_data = {
            "ordnance_type": "ART",
            "ordnance_condition": "INT",
            "is_loaded": True,
            "proximity_to_civilians": "NEA",
            "burial_status": "BUR",
        }

        response = client.post(verify_url, data=verification_data, format="json")

        # CORRECTED LINE: The verify endpoint creates a new UXORecord,
        # so the correct success status is 201 CREATED.
        assert response.status_code == status.HTTP_201_CREATED

        assert UXORecord.objects.count() == 1
        new_uxo_record = UXORecord.objects.first()

        citizen_report.refresh_from_db()
        assert citizen_report.status == "verified"
        assert citizen_report.verified_record == new_uxo_record

        assert new_uxo_record.ordnance_type == "ART"
        assert new_uxo_record.danger_score is not None
        assert new_uxo_record.danger_score > 0
