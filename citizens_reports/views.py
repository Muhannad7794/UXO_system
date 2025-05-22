from rest_framework import generics, permissions, status
from .models import CitizenReport
from .serializers import CitizenReportSerializer, UXORecordFromReportSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_framework.generics import DestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from uxo_records.models import UXORecord
from uxo_records.serializers import UXORecordSerializer


class SubmitCitizenReportView(generics.CreateAPIView):
    queryset = CitizenReport.objects.all()
    serializer_class = CitizenReportSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Submit a new UXO report (citizen)",
        description="Allows a citizen to submit a UXO report including image and location.\n"
        "Status is automatically set to 'pending'.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ListAllCitizenReportsView(generics.ListAPIView):
    queryset = CitizenReport.objects.all()
    serializer_class = CitizenReportSerializer
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        summary="List all citizen reports (admin only)",
        description="Returns a list of all citizen-submitted reports for review.\n"
        "Only accessible to admin users.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RetrieveCitizenReportByIdView(generics.RetrieveAPIView):
    queryset = CitizenReport.objects.all()
    serializer_class = CitizenReportSerializer
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        summary="Retrieve specific citizen report (admin only)",
        description="Returns full details of a specific citizen-submitted report by ID.\n"
        "Only accessible to admin users.",
        parameters=[
            OpenApiParameter(
                name="id",
                description="ID of the citizen report",
                required=True,
                type=int,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DeleteCitizenReportView(DestroyAPIView):
    queryset = CitizenReport.objects.all()
    serializer_class = CitizenReportSerializer
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        summary="Delete a citizen report (admin only)",
        description=(
            "Allows an admin to delete a citizen-submitted report from the system. "
            "Use this if the report was reviewed and determined not to be a valid UXO finding."
        ),
        parameters=[
            OpenApiParameter(
                name="id",
                description="ID of the citizen report to delete",
                required=True,
                type=int,
            ),
        ],
        responses={204: None},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class VerifyCitizenReportView(generics.CreateAPIView):
    queryset = CitizenReport.objects.all()
    serializer_class = UXORecordFromReportSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_url_kwarg = "pk"

    @extend_schema(
        summary="Verify a citizen report",
        description="Admin fills UXO fields. Region is pre-filled from citizen report. Creates UXO record, triggers danger score, and sets report as verified.",
        responses={201: UXORecordFromReportSerializer},
    )
    def post(self, request, *args, **kwargs):
        report = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(region=report.location)

        report.status = "verified"
        report.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
