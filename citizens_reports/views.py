# citizens_reports/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import CitizenReport
from uxo_records.models import UXORecord, Region  # Import Region for the spatial join
from .serializers import (
    CitizenReportSerializer,
    AdminCitizenReportSerializer,
    ReportVerificationSerializer,
)


class SubmitCitizenReportView(generics.CreateAPIView):
    """
    Public view for citizens to submit a new report. (No changes needed)
    """

    queryset = CitizenReport.objects.all()
    serializer_class = CitizenReportSerializer
    permission_classes = [permissions.AllowAny]


class ListCitizenReportsView(generics.ListAPIView):
    """
    Admin-only view to list all citizen reports for review. (No changes needed)
    """

    queryset = CitizenReport.objects.all().order_by("status", "-date_reported")
    serializer_class = AdminCitizenReportSerializer
    permission_classes = [permissions.IsAdminUser]


class RetrieveDeleteCitizenReportView(generics.RetrieveDestroyAPIView):
    """
    Admin-only view to retrieve or delete a single report. (No changes needed)
    """

    queryset = CitizenReport.objects.all()
    serializer_class = AdminCitizenReportSerializer
    permission_classes = [permissions.IsAdminUser]


# --- REFACTORED VERIFICATION VIEW ---
class VerifyCitizenReportView(generics.GenericAPIView):
    """
    Admin-only view to verify a report.
    - GET: Renders a form with fields from the new ReportVerificationSerializer.
    - POST: Creates a new UXORecord using the report's location and the admin's data.
    """

    queryset = CitizenReport.objects.all()
    serializer_class = ReportVerificationSerializer  # Use the new serializer
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

        # The report's location is the single source of truth for the incident's position.
        location_point = report.location

        try:
            # Spatially determine the region this point belongs to.
            containing_region = Region.objects.filter(
                geometry__contains=location_point
            ).first()
            if not containing_region:
                return Response(
                    {
                        "error": f"The location provided ({location_point.wkt}) does not fall within any known Region."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create a new UXORecord using the report's location and the admin's form data.
            new_uxo_record = UXORecord.objects.create(
                location=location_point,
                region=containing_region,
                ordnance_type=admin_data["ordnance_type"],
                ordnance_condition=admin_data["ordnance_condition"],
                is_loaded=admin_data["is_loaded"],
                proximity_to_civilians=admin_data["proximity_to_civilians"],
                burial_status=admin_data["burial_status"],
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
