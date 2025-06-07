# uxo_records/views.py

from rest_framework import viewsets, permissions, filters, mixins
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from .models import UXORecord

# Import both serializers
from .serializers import UXORecordSerializer, UXORecordWriteSerializer
from .filters import UXORecordFilter


class UXORecordPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class UXORecordViewSet(
    viewsets.ModelViewSet
):  # Using ModelViewSet is fine with this pattern
    """
    API endpoint for viewing and managing UXO records.
    Uses different serializers for reading vs. writing data to avoid schema errors.
    """

    queryset = UXORecord.objects.all().order_by("-danger_score", "-id")
    permission_classes = [permissions.IsAdminUser]
    pagination_class = UXORecordPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = UXORecordFilter
    search_fields = ["region__name", "ordnance_type"]
    ordering_fields = ["id", "region__name", "danger_score", "date_reported"]

    def get_serializer_class(self):
        """
        Choose a serializer based on the action.
        - Use the simpler 'Write' serializer for create, update actions.
        - Use the 'GeoFeature' serializer for list, retrieve actions.
        """
        if self.action in ["create", "update", "partial_update"]:
            return UXORecordWriteSerializer
        return UXORecordSerializer
