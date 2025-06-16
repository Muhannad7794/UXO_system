# citizens_reports/tests/factories.py

import factory
from factory.django import DjangoModelFactory, ImageField
from faker import Faker
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point

from ..models import CitizenReport

# We need the RegionFactory from the uxo_records app's test utilities
from uxo_records.tests.factories import RegionFactory

fake = Faker()
User = get_user_model()


class UserFactory(DjangoModelFactory):
    """A factory for creating regular, non-admin User instances."""

    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    is_staff = False
    is_superuser = False

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        self.set_password(extracted or "defaultpassword")
        self.save()


class AdminUserFactory(UserFactory):
    """
    A factory that inherits from UserFactory to create admin users
    with staff and superuser privileges.
    """

    is_staff = True
    is_superuser = True


class CitizenReportFactory(DjangoModelFactory):
    """A factory for creating CitizenReport instances for testing."""

    class Meta:
        model = CitizenReport

    name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_number = factory.Faker("phone_number")
    national_nr = factory.Faker("ssn")

    description = factory.Faker(
        "paragraph",
        nb_sentences=3,
        variable_nb_sentences=True,
    )

    location = factory.LazyFunction(lambda: Point(0.5, 0.5, srid=4326))

    image = ImageField(
        color="red",
        width=100,
        height=100,
        filename="test_image.png",
    )

    # This is the corrected line. It uses the string literal "pending"
    # because your model defines choices as a list of tuples, not a nested class.
    status = "pending"

    verified_record = None
