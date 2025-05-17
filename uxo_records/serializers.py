from rest_framework import serializers
from .models import UXORecord


class UXORecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UXORecord
        fields = [
            "id",
            "region",
            "environmental_conditions",
            "ordnance_type",
            "burial_depth_cm",
            "ordnance_condition",
            "ordnance_age",
            "population_estimate",
        ]
