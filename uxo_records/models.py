# uxo_records/models.py

from django.contrib.gis.db import models as gis_models  # Import GeoDjango models
from django.db import models

# The danger_score calculation will be handled by signals, similar to the original setup.


class UXORecord(models.Model):
    # Fields from the original model
    region = models.CharField(
        max_length=100, help_text="Name of the region for this record"
    )
    environmental_conditions = models.CharField(max_length=100)
    ordnance_type = models.CharField(max_length=100)
    burial_depth_cm = models.CharField(
        max_length=20, help_text="e.g., '15' or '10-20'"
    )  # Keep as CharField for now to match CSV
    ordnance_condition = models.CharField(max_length=50)
    ordnance_age = models.CharField(
        max_length=20, help_text="e.g., '5' or '5-7'"
    )  # Keep as CharField
    population_estimate = models.PositiveIntegerField(
        help_text="Population estimate relevant to this specific UXO context/area"
    )
    uxo_count = models.CharField(
        max_length=50, help_text="e.g., '5' or '10-20' or 'High density...'"
    )  # Keep as CharField

    # Danger score for this specific UXO record/instance
    danger_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Calculated danger score for this specific UXO record",
    )

    # GIS field to store the geometry associated with this record's region
    # This will store the polygon from the CSV data.
    # Making it nullable and blankable for flexibility, though your CSV provides it.
    geometry = gis_models.MultiPolygonField(
        srid=4326,
        null=True,
        blank=True,
        help_text="The geometric shape (polygon) of the region associated with this record.",
    )

    class Meta:
        verbose_name = "UXO Record"
        verbose_name_plural = "UXO Records"
        indexes = [
            models.Index(fields=["region"]),  # Index on the CharField region name
            models.Index(fields=["ordnance_type"]),
            models.Index(
                fields=["danger_score"]
            ),  # Index on danger_score for querying/sorting
            # A spatial index will be automatically created for the 'geometry' field by PostGIS
        ]
        ordering = ["-danger_score", "-id"]  # Example: order by danger score primarily

    def __str__(self):
        return f"{self.ordnance_type} ({self.ordnance_condition}) in {self.region} - Score: {self.danger_score:.2f}"

    # The logic to calculate danger_score will be in signals.py,
    # triggered on pre_save, similar to your original setup.
