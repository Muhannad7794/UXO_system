# uxo_records/serializers.py

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import UXORecord


class UXORecordSerializer(GeoFeatureModelSerializer):
    """
    A GeoJSON serializer for the UXORecord model.
    This is the primary, functional serializer for the API.
    """

    # Explicitly define the 'id' field to ensure drf-spectacular compatibility.
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = UXORecord
        geo_field = "location"  # The geometry field is now 'location'
        id_field = "id"
        fields = [
            "id",
            "region",
            "ordnance_type",
            "ordnance_condition",
            "is_loaded",
            "proximity_to_civilians",
            "burial_status",
            "date_reported",
            "location",
            "danger_score",
        ]


class UXORecordPropertiesSerializer(serializers.ModelSerializer):
    """
    A simple, non-GIS serializer for UXORecord.
    Its only purpose is to be used by drf-spectacular to avoid a bug
    when generating the schema for endpoints that return GeoJSON.
    """

    class Meta:
        model = UXORecord
        # Exclude the geometry field to keep it simple
        exclude = ["location"]
