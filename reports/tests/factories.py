# reports/tests/factories.py

import factory
from factory.django import DjangoModelFactory
from django.contrib.gis.geos import Polygon

# Import the model this factory will create
from ..models import HotZone


class HotZoneFactory(DjangoModelFactory):
    """
    Factory for creating HotZone model instances for testing.
    """

    class Meta:
        model = HotZone

    # Provide default values for the HotZone fields
    geometry = factory.LazyFunction(
        lambda: Polygon.from_bbox((0, 0, 1, 1))  # lon, lat, lon, lat
    )
    record_count = factory.Faker("random_int", min=5, max=50)
    avg_danger_score = factory.Faker(
        "pyfloat", left_digits=1, right_digits=2, min_value=0.1, max_value=0.9
    )
