# danger_score/tests/factories.py

import factory
from factory.django import DjangoModelFactory
from faker import Faker
from django.contrib.gis.geos import Point, Polygon, MultiPolygon

# We need to import the models from the uxo_records app
from uxo_records.models import Region, UXORecord

# Initialize a Faker instance to generate random data
fake = Faker()


class RegionFactory(DjangoModelFactory):
    """
    A factory for creating Region model instances for testing.
    """

    class Meta:
        model = Region
        # Ensure that the 'name' field is unique for each created instance
        django_get_or_create = ("name",)

    # Use factory.Sequence to ensure each region gets a unique name (e.g., "Region 1", "Region 2")
    # This prevents database errors for the unique=True constraint on the name field.
    name = factory.Sequence(lambda n: f"Test Region {n}")

    # Use factory.LazyFunction to generate a simple, valid polygon geometry for the region.
    # This creates a 1x1 degree square, which is sufficient for testing.
    geometry = factory.LazyFunction(
        lambda: MultiPolygon(Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0))))
    )


class UXORecordFactory(DjangoModelFactory):
    """
    A factory for creating UXORecord model instances for testing.
    This factory provides sensible defaults for all required fields.
    """

    class Meta:
        model = UXORecord

    # Use a fixed point for consistency in unit tests.
    location = factory.LazyFunction(lambda: Point(0.5, 0.5, srid=4326))

    # By using SubFactory, creating a UXORecord will automatically create
    # a corresponding Region for it and link them correctly.
    region = factory.SubFactory(RegionFactory)

    # Use Faker to randomly select a valid choice from the model's choices.
    # This makes our tests more robust as they will run against varied data.
    ordnance_type = fake.random_element(
        elements=[c[0] for c in UXORecord.OrdnanceType.choices]
    )
    ordnance_condition = fake.random_element(
        elements=[c[0] for c in UXORecord.OrdnanceCondition.choices]
    )
    proximity_to_civilians = fake.random_element(
        elements=[c[0] for c in UXORecord.ProximityStatus.choices]
    )
    burial_status = fake.random_element(
        elements=[c[0] for c in UXORecord.BurialStatus.choices]
    )

    is_loaded = fake.boolean()

    # The danger_score is intentionally left as None by default,
    # as our tests will be verifying its calculation.
    danger_score = None
