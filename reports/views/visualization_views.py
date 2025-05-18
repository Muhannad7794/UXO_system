# reports/views/visualization_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Count, Avg
from uxo_records.models import UXORecord
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


@extend_schema(
    summary="Heatmap Data",
    description="Returns count values for each (x, y) pair to support heatmap visualizations.",
    parameters=[
        OpenApiParameter(
            name="x",
            description="Field name for X-axis (e.g., 'region', 'ordnance_type')",
            required=True,
            type=str,
            examples=[OpenApiExample(name="X-axis Example", value="region")],
        ),
        OpenApiParameter(
            name="y",
            description="Field name for Y-axis (e.g., 'ordnance_condition', 'ordnance_type')",
            required=True,
            type=str,
            examples=[
                OpenApiExample(name="Y-axis Example", value="ordnance_condition")
            ],
        ),
    ],
)
class HeatmapDataView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        x_field = request.query_params.get("x")
        y_field = request.query_params.get("y")

        if not x_field or not y_field:
            return Response(
                {"error": "Both 'x' and 'y' query parameters are required."}, status=400
            )

        try:
            data = (
                UXORecord.objects.values(x_field, y_field)
                .annotate(count=Count("id"))
                .order_by(x_field, y_field)
            )
            return Response({"x": x_field, "y": y_field, "data": list(data)})
        except Exception as e:
            return Response({"error": str(e)}, status=400)


@extend_schema(
    summary="Histogram Data",
    description="Returns frequency counts of the selected field for histogram plotting.",
    parameters=[
        OpenApiParameter(
            name="field",
            description="Field name to group values by (e.g., 'danger_score', 'region')",
            required=True,
            type=str,
            examples=[OpenApiExample(name="Histogram Field", value="danger_score")],
        )
    ],
)
class HistogramDataView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        field = request.query_params.get("field")

        if not field:
            return Response({"error": "'field' parameter is required."}, status=400)

        try:
            data = (
                UXORecord.objects.values(field)
                .annotate(count=Count("id"))
                .order_by(field)
            )
            return Response({"field": field, "histogram": list(data)})
        except Exception as e:
            return Response({"error": str(e)}, status=400)


@extend_schema(
    summary="Bar Chart Data",
    description="Returns average values for a given numeric field grouped by a category field.",
    parameters=[
        OpenApiParameter(
            name="category",
            description="Categorical field for X-axis (e.g., 'region', 'ordnance_type')",
            required=True,
            type=str,
            examples=[OpenApiExample(name="Category", value="region")],
        ),
        OpenApiParameter(
            name="value",
            description="Numeric field to calculate average of (e.g., 'danger_score')",
            required=True,
            type=str,
            examples=[OpenApiExample(name="Value", value="danger_score")],
        ),
    ],
)
class BarChartDataView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        category = request.query_params.get("category")
        value = request.query_params.get("value")

        if not category or not value:
            return Response(
                {"error": "'category' and 'value' parameters are required."}, status=400
            )

        try:
            data = (
                UXORecord.objects.values(category)
                .annotate(avg_value=Avg(value))
                .order_by(category)
            )
            return Response({"x": category, "y": value, "bar_chart": list(data)})
        except Exception as e:
            return Response({"error": str(e)}, status=400)


@extend_schema(
    summary="Pie Chart Data",
    description="Returns grouped counts of the selected field for pie chart visualization.",
    parameters=[
        OpenApiParameter(
            name="field",
            description="Field name to group pie slices by (e.g., 'ordnance_type')",
            required=True,
            type=str,
            examples=[OpenApiExample(name="Pie Field", value="ordnance_type")],
        )
    ],
)
class PieChartDataView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        field = request.query_params.get("field")

        if not field:
            return Response({"error": "'field' parameter is required."}, status=400)

        try:
            data = (
                UXORecord.objects.values(field)
                .annotate(count=Count("id"))
                .order_by("-count")
            )
            return Response({"field": field, "pie_chart": list(data)})
        except Exception as e:
            return Response({"error": str(e)}, status=400)
