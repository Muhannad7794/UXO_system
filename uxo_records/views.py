# uxo_records/views.py

from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from .models import UXORecord

# --- FIX: Use the correct serializer name from your serializers.py file ---
from .serializers import UXORecordSerializer
from .filters import UXORecordFilter  # Import our new filter class


class UXORecordPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class UXORecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing UXO records.
    Supports advanced filtering, searching, and ordering.
    """

    queryset = UXORecord.objects.all().order_by("-danger_score", "-id")
    # --- FIX: Use the correct serializer class that we imported ---
    serializer_class = UXORecordSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = UXORecordPagination

    # Define the filter backends to be used
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # Point to our custom FilterSet class in filters.py
    filterset_class = UXORecordFilter

    # Define fields for the general-purpose SearchFilter
    # e.g., /api/v1/records/?search=Cluster
    search_fields = [
        "region",
        "ordnance_type",
        "ordnance_condition",
        "environmental_conditions",
    ]

    # Define fields that can be used for sorting
    # e.g., /api/v1/records/?ordering=danger_score
    ordering_fields = [
        "id",
        "region",
        "population_estimate",
        "danger_score",
        # Note: Sorting on the original text fields for age/depth/count
        # might produce alphabetical, not numerical, order.
        "ordnance_age",
        "burial_depth_cm",
        "uxo_count",
    ]
