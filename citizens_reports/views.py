# citizens_reports/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import CitizenReport
from uxo_records.models import UXORecord
from .serializers import (
    CitizenReportSerializer,
    AdminCitizenReportSerializer,
    ReportVerificationSerializer,
)


class SubmitCitizenReportView(generics.CreateAPIView):
    """
    Public view for citizens to submit a new report.
    Handles POST requests to /api/v1/citizen-reports/submit/
    """

    queryset = CitizenReport.objects.all()
    serializer_class = CitizenReportSerializer
    permission_classes = [permissions.AllowAny]


class ListCitizenReportsView(generics.ListAPIView):
    """
    Admin-only view to list all citizen reports for review.
    Handles GET requests to /api/v1/citizen-reports/review/
    """

    queryset = CitizenReport.objects.all().order_by("status", "-date_reported")
    serializer_class = AdminCitizenReportSerializer
    permission_classes = [permissions.IsAdminUser]


class RetrieveDeleteCitizenReportView(generics.RetrieveDestroyAPIView):
    """
    Admin-only view to retrieve the details of a single report, or to delete it.
    - GET: Shows the full report details.
    - DELETE: Deletes the report if it is deemed invalid.
    The DRF Browsable API will show a "DELETE" button on this view's page.
    """

    queryset = CitizenReport.objects.all()
    serializer_class = AdminCitizenReportSerializer
    permission_classes = [permissions.IsAdminUser]


class VerifyCitizenReportView(generics.GenericAPIView):
    """
    Admin-only view to verify a report.
    - GET: The DRF browsable API will render a form with all fields from ReportVerificationSerializer.
    - POST: The admin submits the form to create a new UXORecord.
    """

    queryset = CitizenReport.objects.all()
    serializer_class = ReportVerificationSerializer
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        summary="Verify Citizen Report & Create UXO Record",
        description="Fill out the form to provide the necessary details. Submitting will create a new, official UXORecord and mark this report as 'verified'.",
    )
    def post(self, request, *args, **kwargs):
        report = self.get_object()

        if report.status != "pending":
            return Response(
                {"error": "This report has already been processed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        verification_serializer = self.get_serializer(data=request.data)
        verification_serializer.is_valid(raise_exception=True)
        admin_data = verification_serializer.validated_data

        try:
            # Create a new UXORecord using all the data from the admin's form
            new_uxo_record = UXORecord.objects.create(
                region=admin_data["region"],
                environmental_conditions=admin_data["environmental_conditions"],
                ordnance_type=admin_data["ordnance_type"],
                burial_depth_cm=admin_data["burial_depth_cm"],
                ordnance_condition=admin_data["ordnance_condition"],
                ordnance_age=admin_data["ordnance_age"],
                population_estimate=admin_data["population_estimate"],
                uxo_count=admin_data["uxo_count"],
                # NOTE: The UXORecord 'geometry' (MultiPolygon of the region) is left null.
                # It is not the same as the CitizenReport 'location' (Point of the sighting).
                # The danger_score will be calculated automatically by the model's signal.
            )

            # Update the report's status and link it to the new record
            report.status = "verified"
            report.verified_record = new_uxo_record
            report.save()

            return Response(
                {
                    "status": "Report verified successfully.",
                    "uxo_record_id": new_uxo_record.id,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to create UXO record: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
