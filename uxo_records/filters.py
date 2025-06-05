# uxo_records/filters.py

import django_filters
from .models import UXORecord


class UXORecordFilter(django_filters.FilterSet):
    """
    Custom FilterSet for the UXORecord model.
    This class defines the specific filter lookups available for the API,
    including range filters for numeric fields.
    """

    # Add range filters for numeric fields. This allows filtering with a single query param,
    # e.g., ?danger_score=0.5,0.8 will find scores between 0.5 and 0.8.
    danger_score = django_filters.RangeFilter()
    population_estimate = django_filters.RangeFilter()

    # Note: If you create cleaned numeric fields for age, depth, and count, you can add them here too.
    # For example:
    # ordnance_age_val = django_filters.RangeFilter()
    # burial_depth_cm_val = django_filters.RangeFilter()
    # uxo_count_val = django_filters.RangeFilter()

    # Define case-insensitive text searching for specific fields.
    region = django_filters.CharFilter(lookup_expr="icontains")
    ordnance_type = django_filters.CharFilter(lookup_expr="icontains")
    ordnance_condition = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = UXORecord
        # Define all fields that can be used for filtering.
        fields = [
            "danger_score",
            "population_estimate",
            "region",
            "ordnance_type",
            "ordnance_condition",
        ]
