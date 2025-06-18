# citizens_reports/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import CitizenReport
from uxo_records.models import UXORecord, Region
from .serializers import (
    CitizenReportSerializer,
    AdminCitizenReportSerializer,
    ReportVerificationSerializer,
)
from .forms import ReportVerificationForm
from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import Point
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView


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


# --- VERIFICATION VIEW ---
class VerifyCitizenReportView(generics.GenericAPIView):
    """
    Admin-only view to verify a report.
    - GET: Renders a form with fields from the new ReportVerificationSerializer.
    - POST: Creates a new UXORecord using the report's location and the admin's data.
    """

    queryset = CitizenReport.objects.all()
    serializer_class = ReportVerificationSerializer
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        report = self.get_object()
        context = {
            "report": report,
            "form": ReportVerificationForm(),
        }
        return render(request, "citizens_reports/verification_form.html", context)

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


# ==== Web Views to serve the Frontend ====
class CitizenReportFormView(View):
    """
    Handles the submission from the public-facing HTML form.
    Receives all reporter details, image, and location data.
    """

    def post(self, request, *args, **kwargs):
        # --- Get all the data from the form ---
        name = request.POST.get("name")
        last_name = request.POST.get("last_name")
        national_nr = request.POST.get("national_nr")
        phone_number = request.POST.get("phone_number")
        description = request.POST.get("description")
        location_str = request.POST.get("location")
        image = request.FILES.get("image")

        # --- Basic validation for required fields ---
        if not all([name, last_name, national_nr, description, location_str]):
            # In a real app, you would return a more specific error message
            return render(request, "citizens_reports/partials/report_error.html")

        # --- Create a GIS Point object from the "lat,lng" string ---
        try:
            lat_str, lng_str = location_str.split(",")
            location_point = Point(float(lng_str), float(lat_str), srid=4326)
        except (ValueError, IndexError):
            return render(request, "citizens_reports/partials/report_error.html")

        # --- Create the CitizenReport object in the database with all fields ---
        CitizenReport.objects.create(
            name=name,
            last_name=last_name,
            national_nr=national_nr,
            phone_number=phone_number,
            description=description,
            location=location_point,
            image=image,
        )

        # Render and return the success message HTML snippet
        return render(request, "citizens_reports/partials/report_success.html")


class PendingReportsListView(LoginRequiredMixin, ListView):
    """
    Admin-only page to list all citizen reports with a 'pending' status.
    """

    model = CitizenReport
    template_name = "citizens_reports/review_list.html"
    context_object_name = (
        "pending_reports"  # Name for the list of reports in the html template
    )

    def get_queryset(self):
        """
        Override the default queryset to only return pending reports.
        """
        return CitizenReport.objects.filter(status="pending").order_by("date_reported")


class PendingReportDetailView(LoginRequiredMixin, DetailView):
    """
    Admin-only page to display the details of a single pending citizen report.
    """

    model = CitizenReport
    template_name = "citizens_reports/review_detail.html"
    context_object_name = "report"

    def get_queryset(self):
        """
        Ensure admins can only view pending reports on this page.
        """
        return CitizenReport.objects.filter(status="pending")


class RejectReportView(LoginRequiredMixin, View):
    """
    Handles the POST request to reject a citizen report.
    """

    def post(self, request, *args, **kwargs):
        # Get the primary key from the URL
        report_id = self.kwargs.get("pk")
        # Safely get the report object or return a 404 error
        report = get_object_or_404(CitizenReport, pk=report_id)

        # Update the status and save
        report.status = "rejected"
        report.save()

        # Return an empty response, which HTMX will use to remove the element
        return HttpResponse("")
