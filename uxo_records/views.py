# in uxo_records/views.py

from rest_framework import viewsets, permissions
from rest_framework.decorators import action  # <-- IMPORT THIS
from rest_framework.response import Response  # <-- IMPORT THIS
from rest_framework.pagination import PageNumberPagination  # Make sure this is imported
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import UXORecord
from .serializers import UXORecordSerializer, UXORecordWriteSerializer
from .filters import UXORecordFilter


class UXORecordPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class UXORecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and managing UXO records.
    Uses different serializers for reading vs. writing data to avoid schema errors.
    """

    queryset = UXORecord.objects.all().order_by("-danger_score", "-id")
    permission_classes = [permissions.IsAdminUser]
    pagination_class = UXORecordPagination  # <-- Keep this for the main endpoint
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

    # v-- ADD THIS NEW METHOD --v
    @action(detail=False, methods=["get"], pagination_class=None)
    def all_records(self, request):
        """
        Custom endpoint to return all records without pagination,
        specifically for map visualization.
        """
        queryset = self.get_queryset()
        filtered_queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(filtered_queryset, many=True)
        return Response(serializer.data)
