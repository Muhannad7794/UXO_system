# citizens_reports/serializers.py

from rest_framework import serializers
from rest_framework_gis.serializers import GeometryField
from .models import CitizenReport
from uxo_records.models import UXORecord  # Import UXORecord to access its choices


class CitizenReportSerializer(serializers.ModelSerializer):
    """
    Serializer for citizens submitting a new report. (No changes needed)
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
    Serializer for admins reviewing citizen reports. (No changes needed)
    """

    location = GeometryField()
    verified_record = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CitizenReport
        fields = "__all__"


# --- REFACTORED VERIFICATION SERIALIZER ---
class ReportVerificationSerializer(serializers.Serializer):
    """
    Defines the data an admin must provide to create a UXORecord from a report.
    The fields now match the current UXORecord model and use ChoiceFields
    to render as dropdowns in the DRF browsable API.
    """

    # These fields correspond to the Threat and Vulnerability parameters
    # required by the UXORecord model.
    ordnance_type = serializers.ChoiceField(choices=UXORecord.OrdnanceType.choices)
    ordnance_condition = serializers.ChoiceField(
        choices=UXORecord.OrdnanceCondition.choices
    )
    is_loaded = serializers.BooleanField(
        default=True, help_text="Is the ordnance considered to be loaded and fuzed?"
    )
    proximity_to_civilians = serializers.ChoiceField(
        choices=UXORecord.ProximityStatus.choices
    )
    burial_status = serializers.ChoiceField(choices=UXORecord.BurialStatus.choices)

    # These methods are required by DRF's base Serializer class but we don't need custom logic.
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
