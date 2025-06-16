# uxo_records/urls.py (Corrected)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UXORecordViewSet, UXOBulkUploadView

# Initialize the router
router = DefaultRouter()

# Register the ViewSet. This will automatically create the standard CRUD routes.
router.register(r"", UXORecordViewSet, basename="uxorecord")

# Defining a separate list for custom, non-router paths
# This ensures it is always checked by Django's URL resolver.
urlpatterns = [
    path("bulk-upload-csv/", UXOBulkUploadView.as_view(), name="uxo-bulk-upload"),
]

# Add the router-generated URLs to the urlpatterns list.
# By including the router's URLs AFTER custom path, it is guaranteed that
# the specific 'bulk-upload-csv/' path is matched first.
urlpatterns += router.urls
