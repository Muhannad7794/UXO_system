# uxo_records/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UXORecordViewSet  # Import the single ViewSet

# Create a router and register our viewsets with it.
# DefaultRouter automatically creates the URL patterns for all standard actions
# (list, create, retrieve, update, partial_update, destroy).
router = DefaultRouter()
router.register(r"records", UXORecordViewSet, basename="uxorecord")
# The 'basename' is used for generating URL names if needed, e.g., 'uxorecord-list', 'uxorecord-detail'.

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
]
