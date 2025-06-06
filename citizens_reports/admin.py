# citizens_reports/admin.py

from django.contrib import admin

# Use LeafletGeoAdmin for an interactive map widget
from leaflet.admin import LeafletGeoAdmin
from .models import CitizenReport


@admin.register(CitizenReport)
class CitizenReportAdmin(LeafletGeoAdmin):  # Inherit from LeafletGeoAdmin
    """
    Admin configuration for CitizenReport model.
    Includes an interactive map for the location field and displays all new fields.
    """

    list_display = (
        "id",
        "name",
        "last_name",
        "status",
        "date_reported",
        "has_image",
    )
    list_filter = ("status", "date_reported")
    search_fields = ("name", "last_name", "national_nr", "description")

    # Make fields read-only in the admin detail view as they are set programmatically
    readonly_fields = ("date_reported", "verified_record")

    # Settings for the Leaflet map widget
    settings_overrides = {
        "DEFAULT_CENTER": (33.51, 36.27),  # Default center of the map (e.g., Damascus)
        "DEFAULT_ZOOM": 10,
    }

    def has_image(self, obj):
        return bool(obj.image)

    has_image.boolean = True
    has_image.short_description = "Image Provided"
