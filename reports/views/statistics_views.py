# reports/views/statistics_views.py

from django.db.models import Avg, Count, Max, Min, Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from uxo_records.models import UXORecord
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

# A dictionary to map string parameters to Django's aggregation functions
# This is safer than using getattr() and prevents arbitrary function calls.
AGGREGATION_MAP = {
    "avg": Avg,
    "max": Max,
    "min": Min,
    "sum": Sum,
    "count": Count,
}

# Define which fields are safe and valid for certain operations
VALID_GROUPING_FIELDS = [
    "region",
    "ordnance_type",
    "ordnance_condition",
    "environmental_conditions",
]
VALID_NUMERIC_FIELDS = [
    "danger_score",
    "population_estimate",
    "burial_depth_cm_val",  # Assuming you add this numeric field in the future
    "ordnance_age_val",  # Assuming you add this numeric field in the future
    "uxo_count_val",  # Assuming you add this numeric field in the future
]


@extend_schema(
    summary="Generate UXO Statistics",
    description="""
A flexible endpoint to generate various statistics about UXO records.
Supports two main analysis types: 'aggregate' and 'grouped'.

**1. Aggregate Analysis (`analysis_type=aggregate`):**
Performs a single aggregation over the entire dataset.
- `numeric_field`: The field to aggregate (e.g., 'danger_score').
- `operation`: The function to apply ('avg', 'max', 'min', 'sum', 'count').

*Example: `/api/v1/reports/statistics/?analysis_type=aggregate&numeric_field=danger_score&operation=avg`*

**2. Grouped Analysis (`analysis_type=grouped`):**
Groups data by a category and performs an aggregation on each group.
- `group_by`: The field to group results by (e.g., 'region', 'ordnance_type').
- `aggregate_op` (optional): The function for aggregation ('avg', 'sum', 'max', 'min'). Defaults to 'count' if not provided.
- `aggregate_field` (optional): The numeric field for aggregation. Required if `aggregate_op` is not 'count'.

*Example 1 (Grouped Count): `/api/v1/reports/statistics/?analysis_type=grouped&group_by=ordnance_type`*
*Example 2 (Grouped Average): `/api/v1/reports/statistics/?analysis_type=grouped&group_by=region&aggregate_op=avg&aggregate_field=danger_score`*
    """,
    parameters=[
        OpenApiParameter(
            name="analysis_type",
            description="Type of analysis: 'aggregate' or 'grouped'",
            required=True,
            type=str,
            examples=[
                OpenApiExample(
                    name="Aggregate Analysis",
                    value="aggregate",
                    summary="Overall Stats",
                ),
                OpenApiExample(
                    name="Grouped Analysis", value="grouped", summary="Grouped Stats"
                ),
            ],
        ),
        OpenApiParameter(
            name="group_by",
            description="Field to group by (for 'grouped' analysis).",
            type=str,
        ),
        OpenApiParameter(
            name="numeric_field",
            description="Field for calculation (for 'aggregate' analysis).",
            type=str,
        ),
        OpenApiParameter(
            name="operation",
            description="Aggregation function for 'aggregate' analysis (avg, max, min, sum, count).",
            type=str,
        ),
        OpenApiParameter(
            name="aggregate_field",
            description="Field for calculation within groups (for 'grouped' analysis).",
            type=str,
        ),
        OpenApiParameter(
            name="aggregate_op",
            description="Aggregation function for groups (avg, max, min, sum). Defaults to 'count'.",
            type=str,
        ),
    ],
    tags=["Reports & Analytics"],
)
class StatisticsView(APIView):
    """
    A consolidated view to handle various statistical aggregations.
    This single view replaces the old AggregationView, GroupedCountView,
    and all chart-specific views (Histogram, Bar, Pie).
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        analysis_type = request.query_params.get("analysis_type")

        if analysis_type == "aggregate":
            return self.perform_aggregate_analysis(request)
        elif analysis_type == "grouped":
            return self.perform_grouped_analysis(request)
        else:
            return Response(
                {
                    "error": "Invalid or missing 'analysis_type' parameter. Must be 'aggregate' or 'grouped'."
                },
                status=400,
            )

    def perform_aggregate_analysis(self, request):
        """
        Handles overall aggregation logic (formerly AggregationView).
        """
        field = request.query_params.get("numeric_field")
        operation_str = request.query_params.get("operation")

        if not field or not operation_str:
            return Response(
                {
                    "error": "'numeric_field' and 'operation' are required for 'aggregate' analysis."
                },
                status=400,
            )

        if field not in VALID_NUMERIC_FIELDS:
            return Response(
                {"error": f"Aggregation on field '{field}' is not supported."},
                status=400,
            )

        operation_func = AGGREGATION_MAP.get(operation_str)
        if not operation_func:
            return Response(
                {"error": f"Unsupported operation: '{operation_str}'."}, status=400
            )

        # The 'count' operation in Django's aggregate is special and doesn't need a distinct field.
        # For other operations, we use the provided field.
        aggregation_arg = "id" if operation_str == "count" else field
        result = UXORecord.objects.aggregate(result=operation_func(aggregation_arg))

        return Response(
            {
                "analysis_type": "aggregate",
                "parameters": {"numeric_field": field, "operation": operation_str},
                "result": result.get("result"),
            }
        )

    def perform_grouped_analysis(self, request):
        """
        Handles grouped aggregation logic (formerly GroupedCountView, BarChartDataView, PieChartDataView, etc.).
        """
        group_by = request.query_params.get("group_by")
        aggregate_op_str = request.query_params.get(
            "aggregate_op", "count"
        )  # Default to 'count'
        aggregate_field = request.query_params.get("aggregate_field")

        if not group_by:
            return Response(
                {"error": "'group_by' is required for 'grouped' analysis."}, status=400
            )

        if group_by not in VALID_GROUPING_FIELDS:
            return Response(
                {"error": f"Grouping by '{group_by}' is not supported."}, status=400
            )

        # If an aggregation operation other than 'count' is specified, a field must be provided
        if aggregate_op_str != "count" and not aggregate_field:
            return Response(
                {
                    "error": f"'aggregate_field' is required when 'aggregate_op' is '{aggregate_op_str}'."
                },
                status=400,
            )

        if aggregate_field and aggregate_field not in VALID_NUMERIC_FIELDS:
            return Response(
                {
                    "error": f"Aggregation on field '{aggregate_field}' is not supported."
                },
                status=400,
            )

        op_func = AGGREGATION_MAP.get(aggregate_op_str)
        if not op_func:
            return Response(
                {"error": f"Unsupported operation: '{aggregate_op_str}'."}, status=400
            )

        # Base queryset grouped by the specified field
        queryset = UXORecord.objects.values(group_by)

        # Apply the correct annotation
        if aggregate_op_str == "count":
            # This covers the functionality of GroupedCountView, HistogramDataView, and PieChartDataView
            annotation = queryset.annotate(result=Count("id")).order_by("-result")
        else:
            # This covers the functionality of BarChartDataView
            annotation = queryset.annotate(result=op_func(aggregate_field)).order_by(
                "-result"
            )

        return Response(
            {
                "analysis_type": "grouped",
                "parameters": {
                    "group_by": group_by,
                    "aggregate_op": aggregate_op_str,
                    "aggregate_field": aggregate_field,
                },
                "results": list(annotation),
            }
        )
