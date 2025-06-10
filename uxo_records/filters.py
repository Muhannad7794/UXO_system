# In uxo_records/filters.py

import django_filters
from .models import UXORecord

# ADD THIS IMPORT for MultipleChoiceFilter
from django_filters import MultipleChoiceFilter


class UXORecordFilter(django_filters.FilterSet):
    """
    Custom FilterSet for the UXORecord model.
    - Supports multi-select for choice fields.
    - Supports min/max range for danger_score from separate form inputs.
    """

    # --- Use two separate NumberFilters to match the form's min/max inputs ---
    danger_score_min = django_filters.NumberFilter(
        field_name="danger_score", lookup_expr="gte"
    )
    danger_score_max = django_filters.NumberFilter(
        field_name="danger_score", lookup_expr="lte"
    )

    # --- Define choice fields as MultipleChoiceFilter to accept multiple values ---
    ordnance_type = MultipleChoiceFilter(
        choices=UXORecord._meta.get_field("ordnance_type").choices
    )
    ordnance_condition = MultipleChoiceFilter(
        choices=UXORecord._meta.get_field("ordnance_condition").choices
    )
    burial_status = MultipleChoiceFilter(
        choices=UXORecord._meta.get_field("burial_status").choices
    )
    proximity_to_civilians = MultipleChoiceFilter(
        choices=UXORecord._meta.get_field("proximity_to_civilians").choices
    )

    # --- Keep your existing custom filter for region name searching ---
    region = django_filters.CharFilter(
        field_name="region__name", lookup_expr="icontains"
    )

    class Meta:
        model = UXORecord
        # The fields list now only needs to contain fields that don't have a custom definition above.
        fields = [
            "is_loaded",
        ]
