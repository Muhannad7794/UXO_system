# uxo_records/serializers.py

from rest_framework import serializers
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer,
)  # Import for GeoJSON
from .models import UXORecord


class UXORecordSerializer(
    GeoFeatureModelSerializer
):  # Inherit from GeoFeatureModelSerializer
    """
    A GeoJSON serializer for the UXORecord model.
    This will output data in GeoJSON format, where the 'geometry' field
    will be the GeoJSON geometry, and other fields will be in the 'properties'
    of the GeoJSON feature.
    """

    class Meta:
        model = UXORecord
        geo_field = "geometry"  # Specifies which model field contains the geometry
        fields = [
            "id",
            "region",  # This is the CharField from the model
            "environmental_conditions",
            "ordnance_type",
            "burial_depth_cm",
            "ordnance_condition",
            "ordnance_age",
            "population_estimate",
            "uxo_count",
            "danger_score",  # danger_score is back on this model
            "geometry",  # Include the geometry field
        ]
        # If you want to make some fields read-only, you can add:
        # read_only_fields = ('danger_score',) # Example: if danger_score is always set by signals
