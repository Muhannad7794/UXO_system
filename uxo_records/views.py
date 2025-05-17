from rest_framework import generics, permissions, filters
from rest_framework.pagination import PageNumberPagination
from uxo_records.models import UXORecord
from uxo_records.serializers import UXORecordSerializer


class UXORecordPagination(PageNumberPagination):
    page_size = 10  # Default records per page
    page_size_query_param = "page_size"
    max_page_size = 100


class UXORecordListCreateView(generics.ListCreateAPIView):
    queryset = UXORecord.objects.all()
    serializer_class = UXORecordSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = UXORecordPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "region",
        "ordnance_type",
        "ordnance_condition",
    ]
    ordering_fields = [
        "region",
        "burial_depth_cm",
        "ordnance_age",
        "population_estimate",
        "danger_score",
    ]


class UXORecordRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UXORecord.objects.all()
    serializer_class = UXORecordSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
