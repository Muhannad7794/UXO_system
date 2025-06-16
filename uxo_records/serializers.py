# uxo_records/serializers.py

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.fields import GeometryField  # <-- Import GeometryField
from .models import UXORecord


class UXORecordSerializer(GeoFeatureModelSerializer):
    """
    A GeoJSON serializer for READING UXORecord model data.
    This is used for all GET requests.
    """

    class Meta:
        model = UXORecord
        geo_field = "location"
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
        read_only_fields = ["danger_score", "date_reported"]


# --- SERIALIZER FOR WRITE OPERATIONS ---
class UXORecordWriteSerializer(serializers.ModelSerializer):
    """
    A standard serializer for CREATING AND UPDATING UXORecord instances.
    Used for POST, PUT, PATCH requests. drf-spectacular can handle this without errors.
    """

    location = GeometryField()

    class Meta:
        model = UXORecord
        # List only the fields an admin should provide.
        # 'danger_score' and 'date_reported' are excluded because they are set automatically.
        fields = [
            "region",
            "ordnance_type",
            "ordnance_condition",
            "is_loaded",
            "proximity_to_civilians",
            "burial_status",
            "location",
        ]
