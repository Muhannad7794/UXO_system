# reports/views/quantity_filters_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import F
from uxo_records.models import UXORecord
from uxo_records.serializers import UXORecordSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter


@extend_schema(
    tags=["Quantity-Based Filters"],
    parameters=[
        OpenApiParameter(
            name="field",
            description="Feature to sort by (e.g., danger_score, ordnance_age, uxo_count)",
            required=True,
            type=str,
        ),
        OpenApiParameter(
            name="n",
            description="Number of top results to return (default: 10)",
            required=False,
            type=int,
        ),
    ],
    responses=UXORecordSerializer(many=True),
)
class TopNRecordsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        field = request.query_params.get("field")
        n = int(request.query_params.get("n", 10))

        if not hasattr(UXORecord, field):
            return Response({"error": f"Invalid field name: {field}"}, status=400)

        records = UXORecord.objects.order_by(F(field).desc(nulls_last=True))[:n]
        serializer = UXORecordSerializer(records, many=True)
        return Response(serializer.data)


@extend_schema(
    tags=["Quantity-Based Filters"],
    parameters=[
        OpenApiParameter(
            name="field",
            description="Feature to sort by (e.g., danger_score, ordnance_age, uxo_count)",
            required=True,
            type=str,
        ),
        OpenApiParameter(
            name="n",
            description="Number of bottom results to return (default: 10)",
            required=False,
            type=int,
        ),
    ],
    responses=UXORecordSerializer(many=True),
)
class BottomNRecordsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        field = request.query_params.get("field")
        n = int(request.query_params.get("n", 10))

        if not hasattr(UXORecord, field):
            return Response({"error": f"Invalid field name: {field}"}, status=400)

        records = UXORecord.objects.order_by(F(field).asc(nulls_last=True))[:n]
        serializer = UXORecordSerializer(records, many=True)
        return Response(serializer.data)


@extend_schema(
    tags=["Quantity-Based Filters"],
    parameters=[
        OpenApiParameter(
            name="field",
            description="Feature to filter on (e.g., danger_score, uxo_count, ordnance_age)",
            required=True,
            type=str,
        ),
        OpenApiParameter(
            name="operation",
            description="Comparison operator (e.g., gte, lte, gt, lt, exact)",
            required=True,
            type=str,
        ),
        OpenApiParameter(
            name="value",
            description="Threshold value to compare against",
            required=True,
            type=str,
        ),
    ],
    responses=UXORecordSerializer(many=True),
)
class FilterByThresholdView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        field = request.query_params.get("field")
        op = request.query_params.get("operation")  # e.g., gte, lte, gt, lt, exact
        value = request.query_params.get("value")

        if not hasattr(UXORecord, field):
            return Response({"error": f"Invalid field name: {field}"}, status=400)

        try:
            lookup_expr = f"{field}__{op}"
            filtered_records = UXORecord.objects.filter(**{lookup_expr: value})
        except Exception as e:
            return Response({"error": f"Invalid query: {str(e)}"}, status=400)

        serializer = UXORecordSerializer(filtered_records, many=True)
        return Response(serializer.data)


@extend_schema(
    tags=["Quantity-Based Filters"],
    parameters=[
        OpenApiParameter(
            name="field",
            description="Feature to filter on (e.g., danger_score, burial_depth_cm, ordnance_age)",
            required=True,
            type=str,
        ),
        OpenApiParameter(
            name="min",
            description="Minimum value (inclusive)",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="max",
            description="Maximum value (inclusive)",
            required=False,
            type=str,
        ),
    ],
    responses=UXORecordSerializer(many=True),
)
class RangeFilterView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        field = request.query_params.get("field")
        min_val = request.query_params.get("min")
        max_val = request.query_params.get("max")

        if not hasattr(UXORecord, field):
            return Response({"error": f"Invalid field name: {field}"}, status=400)

        try:
            filters = {}
            if min_val is not None:
                filters[f"{field}__gte"] = min_val
            if max_val is not None:
                filters[f"{field}__lte"] = max_val
            results = UXORecord.objects.filter(**filters)
        except Exception as e:
            return Response({"error": f"Invalid range query: {str(e)}"}, status=400)

        serializer = UXORecordSerializer(results, many=True)
        return Response(serializer.data)
