# citizens_reports/admin.py

from django.contrib import admin
from .models import CitizenReport


@admin.register(CitizenReport)
class CitizenReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "location",
        "status",
        "date_reported",
        "has_image",
    )
    list_filter = ("status", "date_reported")
    search_fields = ("location", "description")
    readonly_fields = ("status", "date_reported")  # ✅ Removed 'linked_record'

    def has_image(self, obj):
        return bool(obj.image)

    has_image.boolean = True
    has_image.short_description = "Image Provided"
