# uxo_records/views.py

from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from .models import UXORecord
from .serializers import UXORecordSerializer  # Using the new serializer
from .filters import UXORecordFilter  # Using the new filter class


class UXORecordPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class UXORecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing UXO records based on the new data model.
    Supports advanced filtering, searching, and ordering.
    """

    # Use the new UXORecord model as the source of data
    queryset = UXORecord.objects.all().order_by("-danger_score", "-id")
    serializer_class = UXORecordSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = UXORecordPagination

    # Define the filter backends
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # Point to our custom FilterSet class
    filterset_class = UXORecordFilter

    # Define fields for the general-purpose SearchFilter
    search_fields = [
        "region__name",  # Allow searching by the name of the related region
        "ordnance_type",
        "ordnance_condition",
        "burial_status",
    ]

    # Define fields that can be used for sorting
    ordering_fields = [
        "id",
        "region__name",
        "danger_score",
        "date_reported",
    ]
