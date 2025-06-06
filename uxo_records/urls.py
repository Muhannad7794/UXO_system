# uxo_records/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UXORecordViewSet

router = DefaultRouter()
# Register the updated ViewSet
router.register(r"", UXORecordViewSet, basename="uxorecord")

urlpatterns = [
    path("", include(router.urls)),
]
