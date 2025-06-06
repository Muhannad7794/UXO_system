# citizens_reports/serializers.py

from rest_framework import serializers
from rest_framework_gis.serializers import GeometryField
from .models import CitizenReport


class CitizenReportSerializer(serializers.ModelSerializer):
    """
    Serializer for citizens submitting a new report.
    """

    location = GeometryField()

    class Meta:
        model = CitizenReport
        fields = [
            "id",
            "name",
            "last_name",
            "national_nr",
            "phone_number",
            "location",
            "description",
            "image",
            "status",
            "date_reported",
        ]
        read_only_fields = ["status", "date_reported"]
        extra_kwargs = {
            "name": {"write_only": True},
            "last_name": {"write_only": True},
            "national_nr": {"write_only": True},
            "phone_number": {"write_only": True},
        }


class AdminCitizenReportSerializer(serializers.ModelSerializer):
    """
    Serializer for admins reviewing citizen reports.
    """

    location = GeometryField()
    verified_record = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CitizenReport
        fields = "__all__"


# --- CORRECTED & EXPANDED SERIALIZER ---
class ReportVerificationSerializer(serializers.Serializer):
    """
    Defines the data an admin must provide to turn a report into a full UXORecord.
    This serializer's fields will be rendered as a form in the DRF GUI.
    """

    # The list of fields now matches the UXORecord model
    region = serializers.CharField(required=True)
    environmental_conditions = serializers.CharField(required=True)
    ordnance_type = serializers.CharField(required=True)
    burial_depth_cm = serializers.CharField(
        required=True, help_text="e.g., '15' or '10-20'"
    )
    ordnance_condition = serializers.CharField(required=True)
    ordnance_age = serializers.CharField(required=True, help_text="e.g., '5' or '5-7'")
    population_estimate = serializers.IntegerField(required=True)
    uxo_count = serializers.CharField(required=True, help_text="e.g., '5' or '10-20'")

    # These methods are required by DRF's base Serializer class but we don't need them.
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
