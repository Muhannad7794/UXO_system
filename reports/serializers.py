# reports/serializers.py

from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import HotZone


class HotZoneSerializer(GeoFeatureModelSerializer):
    """
    GeoJSON serializer for the HotZone model.
    """

    class Meta:
        model = HotZone
        geo_field = "geometry"
        fields = ("id", "record_count", "avg_danger_score")
