from django.db import models


class UXORecord(models.Model):
    region = models.CharField(max_length=100)
    environmental_conditions = models.CharField(max_length=100)
    ordnance_type = models.CharField(max_length=100)
    burial_depth_cm = models.CharField(max_length=20)
    ordnance_condition = models.CharField(max_length=50)
    ordnance_age = models.CharField(max_length=20)
    population_estimate = models.PositiveIntegerField()
    danger_score = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "UXO Record"
        verbose_name_plural = "UXO Records"
        indexes = [
            models.Index(fields=["region"]),
            models.Index(fields=["ordnance_type"]),
        ]

    def __str__(self):
        return f"{self.ordnance_type} ({self.ordnance_condition}) in {self.region}"
