# reports/views/statistics_views.py

from django.db.models import Avg, Count, Max, Min, Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from uxo_records.models import UXORecord, Region  # Import Region as well
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

# A dictionary to map string parameters to Django's aggregation functions
AGGREGATION_MAP = {
    "avg": Avg,
    "max": Max,
    "min": Min,
    "sum": Sum,
    "count": Count,
}

# --- UPDATED WHITELISTS FOR THE NEW DATA MODEL ---

# Define which fields are valid for grouping.
# Using 'region__name' allows grouping by the name of the region, which is more useful.
VALID_GROUPING_FIELDS = [
    "region__name",
    "ordnance_type",
    "ordnance_condition",
    "is_loaded",
    "proximity_to_civilians",
    "burial_status",
]

# Define which fields are valid for numeric aggregation.
# In our new model, 'danger_score' is the only relevant numeric field.
VALID_NUMERIC_FIELDS = [
    "danger_score",
]


@extend_schema(
    summary="Generate UXO Statistics",
    description="""
A flexible endpoint to generate various statistics about UXO records based on the new data model.
Supports two main analysis types: 'aggregate' and 'grouped'.

**1. Aggregate Analysis (`analysis_type=aggregate`):**
Performs a single aggregation over the entire dataset.
- `numeric_field`: The field to aggregate (must be 'danger_score').
- `operation`: The function to apply ('avg', 'max', 'min', 'sum', 'count').

*Example: `/api/v1/reports/statistics/?analysis_type=aggregate&numeric_field=danger_score&operation=avg`*

**2. Grouped Analysis (`analysis_type=grouped`):**
Groups data by a category and performs an aggregation on each group.
- `group_by`: The field to group results by (e.g., 'region__name', 'ordnance_type').
- `aggregate_op` (optional): The function for aggregation ('avg', 'sum', 'max', 'min'). Defaults to 'count'.
- `aggregate_field` (optional): The numeric field for aggregation (must be 'danger_score'). Required if `aggregate_op` is not 'count'.

*Example 1 (Grouped Count): `/api/v1/reports/statistics/?analysis_type=grouped&group_by=ordnance_type`*
*Example 2 (Grouped Average): `/api/v1/reports/statistics/?analysis_type=grouped&group_by=region__name&aggregate_op=avg&aggregate_field=danger_score`*
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
            description=f"Field to group by (for 'grouped' analysis). Valid options: {', '.join(VALID_GROUPING_FIELDS)}",
            type=str,
        ),
        OpenApiParameter(
            name="numeric_field",
            description="Field for calculation (for 'aggregate' analysis). Valid options: 'danger_score'",
            type=str,
        ),
        OpenApiParameter(
            name="operation",
            description="Aggregation function for 'aggregate' analysis (avg, max, min, sum, count).",
            type=str,
        ),
        OpenApiParameter(
            name="aggregate_field",
            description="Field for calculation within groups (for 'grouped' analysis). Valid options: 'danger_score'",
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
    A consolidated view to handle various statistical aggregations on the new data model.
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
        Handles overall aggregation logic.
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
                {
                    "error": f"Aggregation on field '{field}' is not supported. Valid field is 'danger_score'."
                },
                status=400,
            )

        operation_func = AGGREGATION_MAP.get(operation_str)
        if not operation_func:
            return Response(
                {"error": f"Unsupported operation: '{operation_str}'."}, status=400
            )

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
        Handles grouped aggregation logic.
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
                    "error": f"Aggregation on field '{aggregate_field}' is not supported. Valid field is 'danger_score'."
                },
                status=400,
            )

        op_func = AGGREGATION_MAP.get(aggregate_op_str)
        if not op_func:
            return Response(
                {"error": f"Unsupported operation: '{aggregate_op_str}'."}, status=400
            )

        queryset = UXORecord.objects.values(group_by)

        if aggregate_op_str == "count":
            annotation = queryset.annotate(result=Count("id")).order_by("-result")
        else:
            annotation = queryset.annotate(result=op_func(aggregate_field)).order_by(
                "-result"
            )

        # To improve readability of the output, we can rename the grouping key
        # from e.g. 'region__name' to 'group' in the final list.
        results_list = []
        for item in annotation:
            results_list.append(
                {"group": item.pop(group_by), "value": item.pop("result")}
            )

        return Response(
            {
                "analysis_type": "grouped",
                "parameters": {
                    "group_by": group_by,
                    "aggregate_op": aggregate_op_str,
                    "aggregate_field": aggregate_field,
                },
                "results": results_list,
            }
        )
