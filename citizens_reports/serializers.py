# citizens_reports/serializers.py
from rest_framework import serializers
from .models import CitizenReport
from uxo_records.models import UXORecord


class CitizenReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CitizenReport
        fields = ["id", "image", "location", "description", "date_reported", "status"]
        read_only_fields = ["status", "date_reported"]


class UXORecordFromReportSerializer(serializers.ModelSerializer):
    region = serializers.CharField(read_only=True)

    class Meta:
        model = UXORecord
        exclude = ["id", "danger_score"]
