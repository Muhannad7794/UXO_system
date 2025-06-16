# citizens_reports/serializers.py

from rest_framework import serializers
from rest_framework_gis.serializers import GeometryField
from .models import CitizenReport
from uxo_records.models import UXORecord


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


class ReportVerificationSerializer(serializers.Serializer):
    """
    This serializer defines the fields for the admin verification form.
    It now correctly pulls choices directly from the UXORecord model's fields.
    """

    ordnance_type = serializers.ChoiceField(
        choices=UXORecord._meta.get_field("ordnance_type").choices,
        style={"base_template": "select.html", "class": "form-select"},
    )
    ordnance_condition = serializers.ChoiceField(
        choices=UXORecord._meta.get_field("ordnance_condition").choices,
        style={"base_template": "select.html", "class": "form-select"},
    )
    is_loaded = serializers.BooleanField(
        label="Is the ordnance considered to be loaded and fuzed?",
        required=False,
        style={"base_template": "checkbox.html", "class": "form-check-input"},
    )
    proximity_to_civilians = serializers.ChoiceField(
        choices=UXORecord._meta.get_field("proximity_to_civilians").choices,
        style={"base_template": "select.html", "class": "form-select"},
    )
    burial_status = serializers.ChoiceField(
        choices=UXORecord._meta.get_field("burial_status").choices,
        style={"base_template": "select.html", "class": "form-select"},
    )
