# uxo_records/filters.py

import django_filters
from .models import UXORecord


class UXORecordFilter(django_filters.FilterSet):
    """
    Custom FilterSet for the new UXORecord model.
    Defines the specific filter lookups available for the API.
    """

    # Filter for danger_score using a numeric range (e.g., ?danger_score=0.5,0.8)
    danger_score = django_filters.RangeFilter()

    # Allow filtering by the related Region's name
    region = django_filters.CharFilter(
        field_name="region__name", lookup_expr="icontains"
    )

    class Meta:
        model = UXORecord
        # Define all fields that can be used for exact-match filtering
        fields = [
            "ordnance_type",
            "ordnance_condition",
            "is_loaded",
            "proximity_to_civilians",
            "burial_status",
            "danger_score",  # Also allows exact match
            "region",  # Allows filtering by region ID
        ]
