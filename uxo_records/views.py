# uxo_records/views.py

from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend # For more advanced filtering

from .models import UXORecord
from .serializers import UXORecordSerializer

# Your custom pagination class - this is fine to keep.
class UXORecordPagination(PageNumberPagination):
    page_size = 10  # Default records per page
    page_size_query_param = "page_size"
    max_page_size = 100


class UXORecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows UXO records to be viewed or edited.
    Each record includes its own geometry and calculated danger_score.
    """
    queryset = UXORecord.objects.all().order_by('-danger_score', '-id') # Default ordering
    serializer_class = UXORecordSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = UXORecordPagination
    
    # Define filter backends: DjangoFilterBackend for specific field lookups,
    # SearchFilter for general search, OrderingFilter for sorting.
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Fields for DjangoFilterBackend (more structured filtering)
    # Allows filtering like /api/v1/records/?region=Aleppo&ordnance_type=Artillery
    # For CharFields like 'region', 'exact' and 'icontains' are common.
    # For FloatField like 'danger_score', 'exact', 'gte', 'lte' are common.
    filterset_fields = {
        'region': ['exact', 'icontains'],
        'ordnance_type': ['exact', 'icontains'],
        'ordnance_condition': ['exact', 'icontains'],
        'environmental_conditions': ['exact', 'icontains'],
        'danger_score': ['exact', 'gte', 'lte', 'gt', 'lt'], # Numeric filtering
        'population_estimate': ['exact', 'gte', 'lte', 'gt', 'lt'],
        # Add other fields as needed
    }

    # Fields for SearchFilter (general search across multiple fields)
    # Allows search like /api/v1/records/?search=Aleppo Artillery
    search_fields = [
        "region",
        "ordnance_type",
        "ordnance_condition",
        "environmental_conditions",
        # Note: Searching directly on geometry fields with SearchFilter is not standard.
        # Spatial searches require dedicated spatial lookups, often via custom filters or specific API params.
    ]

    # Fields for OrderingFilter
    # Allows ordering like /api/v1/records/?ordering=region or /api/v1/records/?ordering=-danger_score
    ordering_fields = [
        "region",
        "burial_depth_cm", # Note: Ordering on CharField might not be numerically accurate if values vary wildly
        "ordnance_age",    # Note: Ordering on CharField might not be numerically accurate
        "population_estimate",
        "danger_score",    # Now a direct field on UXORecord
        "uxo_count",       # Note: Ordering on CharField might not be numerically accurate
        "id"
    ]

    # If you needed to perform spatial queries (e.g., find records within a certain bounding box),
    # you would typically add a custom filter class that uses GeoDjango's spatial lookups.
    # For example, using 'rest_framework_gis.filters.InBBoxFilter':
    # from rest_framework_gis.filters import InBBoxFilter
    # bbox_filter_field = 'geometry' # The geometry field on your model
    # bbox_filter_include_overlapping = True # Optional
    # filter_backends = [InBBoxFilter, DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    #
    # This would allow requests like: /api/v1/records/?in_bbox=xmin,ymin,xmax,ymax

