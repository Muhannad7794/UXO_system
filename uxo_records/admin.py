# uxo_records/admin.py

from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin  # Use GISModelAdmin
from .models import UXORecord


@admin.register(UXORecord)
class UXORecordAdmin(GISModelAdmin):  # Inherit from GISModelAdmin
    """
    Admin interface for the UXORecord model.
    Uses GISModelAdmin to display an interactive map for the geometry field.
    """

    list_display = (
        "id",
        "region",
        "ordnance_type",
        "ordnance_condition",
        "danger_score",  # danger_score is back on this model
        "population_estimate",
        "uxo_count",
        # 'geometry' field is present, but displaying full WKT in list_display is often too verbose.
        # The map widget will appear in the detail/edit form for this record.
        # You could add a method to the model to show if geometry exists, e.g., has_geometry.
    )
    list_filter = ("region", "ordnance_type", "ordnance_condition", "danger_score")
    search_fields = ("region", "ordnance_type", "ordnance_condition")
    ordering = ("-danger_score",)  # Order by danger_score by default in admin list

    # GISModelAdmin will use Leaflet by default for the 'geometry' field widget.
    # You can customize map options if needed:
    # default_lat = 35 # Approximate center for Syria
    # default_lon = 38
    # default_zoom = 5

    # Fields to display in the form. If you want to control the order or which fields appear:
    # fields = ('region', 'geometry', 'danger_score', 'environmental_conditions', ...)
