# citizens_reports/models.py

from django.db import models
from django.contrib.gis.db import models as gis_models


class CitizenReport(models.Model):
    """
    Represents a UXO report submitted by a citizen.
    Includes reporter's information for verification and a precise GIS location.
    """

    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("verified", "Verified - Record Created"),
        ("rejected", "Rejected - Invalid Information"),
    ]

    # === New Reporter Identity Fields ===
    name = models.CharField(max_length=100, help_text="First name of the reporter.")
    last_name = models.CharField(max_length=100, help_text="Last name of the reporter.")
    # Using CharField for flexibility with different national ID formats.
    # Added unique=True to prevent multiple pending reports from the same person.
    national_nr = models.CharField(
        max_length=50,
        unique=True,
        help_text="National number or unique identifier for verification.",
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,  # Making phone number optional
        help_text="Contact phone number of the reporter.",
    )

    # === GIS Integration ===
    # Replaced the simple CharField with a PointField for accurate geospatial data.
    location = gis_models.PointField(
        help_text="The precise latitude and longitude of the reported UXO."
    )

    # === Other Fields ===
    image = models.ImageField(
        upload_to="citizen_reports/",
        help_text="An image of the reported UXO provided by the citizen.",
    )
    description = models.TextField(
        blank=False,  # Making description mandatory for a useful report.
        help_text="Detailed description of the sighting.",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="The current status of the report, managed by admins.",
    )
    date_reported = models.DateTimeField(auto_now_add=True)

    # === New Tracking Field ===
    # This links the report to the official UXORecord once it's verified.
    # This is crucial for tracking and auditing.
    verified_record = models.ForeignKey(
        "uxo_records.UXORecord",
        on_delete=models.SET_NULL,  # If the UXORecord is deleted, keep the report but set this link to null.
        null=True,
        blank=True,
        editable=False,
        help_text="Link to the official UXORecord created from this report upon verification.",
    )

    def __str__(self):
        return f"Report #{self.id} by {self.name} {self.last_name} ({self.status})"

    class Meta:
        ordering = ["-date_reported"]
