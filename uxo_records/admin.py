# uxo_records/admin.py

from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from .models import Region, UXORecord


@admin.register(Region)
class RegionAdmin(LeafletGeoAdmin):
    """
    Admin configuration for the Region model.
    Displays a map for the region's geometry.
    """

    list_display = ("name",)
    search_fields = ("name",)


@admin.register(UXORecord)
class UXORecordAdmin(LeafletGeoAdmin):
    """
    Admin configuration for individual UXO Records.
    Displays a map for the incident's point location.
    """

    list_display = (
        "id",
        "region",
        "ordnance_type",
        "danger_score",
        "is_loaded",
        "burial_status",
        "date_reported",
    )
    list_filter = (
        "region",
        "ordnance_type",
        "ordnance_condition",
        "is_loaded",
        "burial_status",
        "proximity_to_civilians",
    )
    search_fields = ("id", "region__name")
    readonly_fields = ("danger_score", "date_reported")

    # Settings for the Leaflet point map widget
    settings_overrides = {
        "DEFAULT_CENTER": (33.85, 35.86),  # Default center of the map
        "DEFAULT_ZOOM": 8,
    }
