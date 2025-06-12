# in uxo_records/views.py

from rest_framework import viewsets, permissions
from rest_framework.decorators import action  # <-- IMPORT THIS
from rest_framework.response import Response  # <-- IMPORT THIS
from rest_framework.pagination import PageNumberPagination  # Make sure this is imported
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import UXORecord, Region
from .serializers import UXORecordSerializer, UXORecordWriteSerializer
from .filters import UXORecordFilter
import csv
import io
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.contrib.gis.geos import Point


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


class UXOBulkUploadView(APIView):
    """
    An API View to allow admin users to bulk upload UXORecord instances from a CSV file.
    This view automatically determines the correct region using a spatial join and translates
    descriptive text into the required 3-letter codes.
    """

    permission_classes = [IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.data.get("file")

        if not file_obj:
            return Response(
                {"error": "No file was uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not file_obj.name.endswith(".csv"):
            return Response(
                {"error": "This is not a CSV file."}, status=status.HTTP_400_BAD_REQUEST
            )

        # --- Create Reverse Mapping Dictionaries ---
        # This creates dictionaries to translate, e.g., "Artillery Projectile" -> "ART"
        # We make it case-insensitive by converting keys to lowercase.
        ord_type_map = {
            label.lower(): value for value, label in UXORecord.OrdnanceType.choices
        }
        ord_cond_map = {
            label.lower(): value for value, label in UXORecord.OrdnanceCondition.choices
        }
        prox_stat_map = {
            label.lower(): value for value, label in UXORecord.ProximityStatus.choices
        }
        burial_stat_map = {
            label.lower(): value for value, label in UXORecord.BurialStatus.choices
        }

        try:
            decoded_file = file_obj.read().decode("utf-8")
            io_string = io.StringIO(decoded_file)
            # We assume the CSV headers might have spaces or varied casing, so we clean them up.
            cleaned_headers = [h.strip().lower() for h in next(io_string).split(",")]
            io_string.seek(0)  # Reset buffer to the beginning
            next(io_string)  # Skip the original header row

            reader = csv.DictReader(io_string, fieldnames=cleaned_headers)

            created_count = 0
            errors = []

            for row in reader:
                try:
                    # 1. Create the Point object from the coordinates
                    location = Point(
                        float(row.get("longitude")),
                        float(row.get("latitude")),
                        srid=4326,
                    )

                    # 2. Perform the spatial join to find the containing region
                    region = Region.objects.get(geometry__contains=location)

                    # 3. Translate CSV string values to 3-letter codes using the maps
                    ord_type_code = ord_type_map.get(
                        row.get("ordnance_type", "").lower()
                    )
                    ord_cond_code = ord_cond_map.get(
                        row.get("ordnance_condition", "").lower()
                    )
                    prox_stat_code = prox_stat_map.get(
                        row.get("proximity_to_civilians", "").lower()
                    )
                    burial_stat_code = burial_stat_map.get(
                        row.get("burial_status", "").lower()
                    )

                    # Create the UXORecord instance
                    UXORecord.objects.create(
                        region=region,
                        location=location,
                        ordnance_type=ord_type_code,
                        ordnance_condition=ord_cond_code,
                        is_loaded=row.get("is_loaded", "False").lower()
                        in ("true", "1", "t"),
                        proximity_to_civilians=prox_stat_code,
                        burial_status=burial_stat_code,
                    )
                    created_count += 1

                except Region.DoesNotExist:
                    errors.append(
                        f"Row {reader.line_num}: Location ({row.get('latitude')}, {row.get('longitude')}) does not fall within any known region."
                    )
                except Exception as e:
                    errors.append(
                        f"Row {reader.line_num}: An error occurred - {str(e)}"
                    )

            if errors:
                return Response(
                    {
                        "message": f"Process completed with errors. Successfully created {created_count} records.",
                        "errors": errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"message": f"Successfully created {created_count} new UXO records."},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": f"Failed to process file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
