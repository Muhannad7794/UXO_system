from django.contrib import admin
from .models import UXORecord


@admin.register(UXORecord)
class UXORecordAdmin(admin.ModelAdmin):
    list_display = (
        "region",
        "environmental_conditions",
        "ordnance_type",
        "burial_depth_cm",
        "ordnance_condition",
        "ordnance_age",
        "population_estimate",
    )
    list_filter = ("region", "ordnance_type", "ordnance_condition")
    search_fields = ("region", "ordnance_type", "ordnance_condition")
