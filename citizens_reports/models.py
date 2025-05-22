# citizens_reports/models.py
from django.db import models


class CitizenReport(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    ]

    image = models.ImageField(upload_to="citizen_reports/")
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", editable=False
    )
    date_reported = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report #{self.id} - {self.location} ({self.status})"
