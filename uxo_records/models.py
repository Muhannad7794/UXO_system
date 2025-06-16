# uxo_records/models.py

from django.db import models
from django.contrib.gis.db import models as gis_models


class Region(models.Model):
    """
    Represents a single administrative region with its geographic boundary.
    e.g., 'Aleppo Governorate' with its MultiPolygon.
    """

    name = models.CharField(
        max_length=100, unique=True, help_text="Name of the administrative region"
    )
    geometry = gis_models.MultiPolygonField(
        srid=4326, help_text="The geometric shape (polygon) of the region."
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Regions"
        ordering = ["name"]


class UXORecord(models.Model):
    """
    Represents a single, specific UXO incident or report.
    Each record is located at a precise point and belongs to a Region.
    """

    # --- ENUMERATIONS FOR DATA INTEGRITY ---
    class OrdnanceType(models.TextChoices):
        ARTILLERY = "ART", "Artillery Projectile"
        MORTAR = "MOR", "Mortar Bomb"
        ROCKET = "ROC", "Rocket"
        AIRCRAFT_BOMB = "BOM", "Aircraft Bomb"
        LANDMINE = "MIN", "Landmine"
        SUBMUNITION = "SUB", "Submunition"
        IED = "IED", "Improvised Explosive Device"
        OTHER = "OTH", "Other"

    class OrdnanceCondition(models.TextChoices):
        INTACT = "INT", "Intact"
        CORRODED = "COR", "Corroded"
        DAMAGED = "DMG", "Damaged/Deformed"
        LEAKING = "LEK", "Leaking/Exuding"

    class ProximityStatus(models.TextChoices):
        IMMEDIATE = "IMM", "Immediate (0-100m to civilians/infrastructure)"
        NEAR = "NEA", "Near (101-500m)"
        REMOTE = "REM", "Remote (>500m)"

    class BurialStatus(models.TextChoices):
        EXPOSED = "EXP", "Exposed"
        PARTIAL = "PAR", "Partially Exposed"
        CONCEALED = "CON", "Concealed (by vegetation/debris)"
        BURIED = "BUR", "Buried"

    # === CORE FIELDS ===
    location = gis_models.PointField(
        srid=4326, help_text="The precise GIS point location of the UXO incident."
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uxo_records",
        help_text="The administrative region this UXO record belongs to.",
    )
    date_reported = models.DateTimeField(auto_now_add=True)

    # === THREAT PARAMETERS ===
    ordnance_type = models.CharField(max_length=3, choices=OrdnanceType.choices)
    ordnance_condition = models.CharField(
        max_length=3, choices=OrdnanceCondition.choices
    )
    is_loaded = models.BooleanField(
        default=True, help_text="Is the ordnance considered to be loaded and fuzed?"
    )

    # === VULNERABILITY & EXPOSURE PARAMETERS ===
    proximity_to_civilians = models.CharField(
        max_length=3,
        choices=ProximityStatus.choices,
        help_text="General proximity to civilians or critical infrastructure.",
    )
    burial_status = models.CharField(
        max_length=3,
        choices=BurialStatus.choices,
        help_text="How exposed or buried is the ordnance?",
    )
    # === DANGER SCORE ===
    danger_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Calculated danger score for this specific UXO incident.",
    )

    def __str__(self):
        return f"UXO Record #{self.id} in {self.region.name if self.region else 'N/A'}"

    class Meta:
        ordering = ["-danger_score"]
