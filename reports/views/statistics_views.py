# reports/views/statistics_views.py
from django.db.models import Avg, Count, Max, Min
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from uxo_records.models import UXORecord
from drf_spectacular.utils import extend_schema, OpenApiParameter


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="field", description="Field to aggregate", required=True, type=str
        ),
        OpenApiParameter(
            name="operation",
            description="Aggregation operation: average, max, min, count",
            required=True,
            type=str,
        ),
    ]
)
class AggregationView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        field = request.query_params.get("field")
        operation = request.query_params.get("operation")

        if not field or not operation:
            return Response(
                {
                    "error": "Both 'field' and 'operation' query parameters are required."
                },
                status=400,
            )

        numeric_fields = [
            "burial_depth_cm",
            "ordnance_age",
            "population_estimate",
            "danger_score",
        ]

        if field not in numeric_fields:
            return Response({"error": f"Field '{field}' is not supported."}, status=400)

        if operation == "average":
            result = UXORecord.objects.aggregate(avg=Avg(field))
        elif operation == "max":
            result = UXORecord.objects.aggregate(max=Max(field))
        elif operation == "min":
            result = UXORecord.objects.aggregate(min=Min(field))
        elif operation == "count":
            result = UXORecord.objects.aggregate(count=Count(field))
        else:
            return Response(
                {"error": f"Unsupported operation '{operation}'."}, status=400
            )

        return Response({"field": field, "operation": operation, "result": result})


@extend_schema(
    tags=["Statistics"],
    parameters=[
        OpenApiParameter(
            name="group_by",
            description="Feature to group by (e.g., region, ordnance_type, environmental_conditions, ordnance_condition)",
            required=True,
            type=str,
        )
    ],
)
class GroupedCountView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        group_by = request.query_params.get("group_by")

        if not group_by:
            return Response(
                {"error": "'group_by' query parameter is required."}, status=400
            )

        if group_by not in [
            "region",
            "ordnance_type",
            "ordnance_condition",
            "environmental_conditions",
        ]:
            return Response(
                {"error": f"Grouping by '{group_by}' is not supported."}, status=400
            )

        data = (
            UXORecord.objects.values(group_by)
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        return Response({"group_by": group_by, "results": list(data)})
