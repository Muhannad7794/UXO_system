# reports/views/geospatial_views.py

from django.contrib.gis.geos import Polygon
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from uxo_records.models import UXORecord

# --- FIX: Use the correct serializer name from your serializers.py file ---
from uxo_records.serializers import UXORecordSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


@extend_schema(
    summary="Geospatial Heatmap Data",
    description="""
Generates data points for a geospatial heatmap visualization.
Each data point is an array containing `[latitude, longitude, intensity]`.
The intensity is based on the `danger_score` of the UXO record.
This data is formatted for use with common mapping libraries like Leaflet.js with the heatmap plugin.
    """,
    tags=["Reports & Analytics", "Geospatial"],
)
class HeatmapView(APIView):
    """
    Provides data formatted for a geospatial heatmap layer.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        # We only want records that have a geometry and a danger score to be included in the heatmap
        queryset = UXORecord.objects.filter(
            geometry__isnull=False, danger_score__isnull=False
        )

        # Create a list of [latitude, longitude, intensity] for each record
        # We use the centroid of the record's geometry as the point for the heatmap
        heatmap_data = [
            [
                record.geometry.centroid.y,  # Latitude
                record.geometry.centroid.x,  # Longitude
                float(record.danger_score),  # Intensity
            ]
            for record in queryset
        ]

        return Response(heatmap_data)


@extend_schema(
    summary="Filter Records Within a Bounding Box",
    description="""
Retrieves all UXO records whose geometries intersect with a given geographic bounding box.
The bounding box must be specified as a comma-separated string of four coordinates in the format:
`min_longitude,min_latitude,max_longitude,max_latitude`
The response is a GeoJSON FeatureCollection, ready to be rendered on a map.
    """,
    parameters=[
        OpenApiParameter(
            name="bbox",
            description="Bounding box coordinates: min_lon,min_lat,max_lon,max_lat",
            required=True,
            type=str,
            examples=[
                OpenApiExample(
                    name="Bounding Box for Damascus Area",
                    value="36.2,33.4,36.4,33.6",  # Example coordinates
                )
            ],
        )
    ],
    # --- FIX: Use the correct serializer class that we imported ---
    responses=UXORecordSerializer,
    tags=["Reports & Analytics", "Geospatial"],
)
class RecordsWithinBboxView(APIView):
    """
    Filters UXO records that are within a specified geographic bounding box.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        bbox_str = request.query_params.get("bbox")

        if not bbox_str:
            return Response(
                {"error": "The 'bbox' query parameter is required."}, status=400
            )

        try:
            # Parse the bounding box string
            coords = [float(c.strip()) for c in bbox_str.split(",")]
            if len(coords) != 4:
                raise ValueError("Bounding box must contain exactly four coordinates.")

            xmin, ymin, xmax, ymax = coords

            # Create a Polygon object from the bounding box coordinates
            # The SRID 4326 corresponds to WGS 84, the standard for GPS coordinates
            bbox_polygon = Polygon.from_bbox((xmin, ymin, xmax, ymax))
            bbox_polygon.srid = 4326

            # Filter records where the geometry intersects the bounding box
            # This is a powerful database-level spatial query
            queryset = UXORecord.objects.filter(geometry__intersects=bbox_polygon)

            # Serialize the data into GeoJSON format
            # --- FIX: Use the correct serializer class that we imported ---
            serializer = UXORecordSerializer(queryset, many=True)
            return Response(serializer.data)

        except ValueError as e:
            return Response({"error": f"Invalid 'bbox' format. {e}"}, status=400)
        except Exception as e:
            # Catch any other unexpected errors
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"}, status=500
            )
