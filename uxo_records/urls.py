# uxo_records/urls.py (Corrected)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UXORecordViewSet, UXOBulkUploadView

# Initialize the router
router = DefaultRouter()

# Register the ViewSet. The router will create the standard URLs for it
# (e.g., / for list/create, /<pk>/ for retrieve/update/delete, and /all_records/ for the custom action)
router.register(r"", UXORecordViewSet, basename="uxorecord")

# Define a separate list for your custom, non-router paths
# This ensures it is always checked by Django's URL resolver.
urlpatterns = [
    path("bulk-upload-csv/", UXOBulkUploadView.as_view(), name="uxo-bulk-upload"),
]

# Add the router-generated URLs to the urlpatterns list.
# By including the router's URLs *after* your custom path, you guarantee that
# the specific 'bulk-upload-csv/' path is matched first.
urlpatterns += router.urls
