# reports/views/search_sort_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from uxo_records.models import UXORecord
from uxo_records.serializers import UXORecordSerializer
from django.db.models import Q, F
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


@extend_schema(
    tags=["Search & Sort"],
    parameters=[
        OpenApiParameter(
            name="query",
            description="Search term(s) for region, ordnance_type, or ordnance_condition. Can be comma-separated for multiple terms.",
            required=True,
            type=str,
            examples=[
                OpenApiExample(
                    name="Single Search Term", value="Aleppo", parameter_only=True
                ),
                OpenApiExample(
                    name="Multiple Terms", value="Raqqa,Cluster", parameter_only=True
                ),
            ],
        ),
        OpenApiParameter(
            name="order_by",
            description="Field to order the results by (e.g., danger_score, ordnance_age, burial_depth_cm).",
            required=True,
            type=str,
        ),
        OpenApiParameter(
            name="desc",
            description="Set to 'true' for descending or 'false' for ascending sort. Default is true.",
            required=False,
            type=str,
        ),
    ],
    responses=UXORecordSerializer(many=True),
)
class CombinedSearchAndOrderingView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        query = request.query_params.get("query")  # Single term or comma-separated
        order_by = request.query_params.get(
            "order_by"
        )  # e.g. danger_score, ordnance_age
        descending = request.query_params.get("desc", "true").lower() == "true"

        if not query or not order_by:
            return Response(
                {"error": "Both 'query' and 'order_by' parameters are required."},
                status=400,
            )

        terms = [q.strip() for q in query.split(",") if q.strip()]

        if not hasattr(UXORecord, order_by):
            return Response(
                {"error": f"Invalid field to order by: {order_by}"}, status=400
            )

        # Build Q object dynamically (OR conditions)
        filters = Q()
        for term in terms:
            filters |= Q(region__icontains=term)
            filters |= Q(ordnance_type__icontains=term)
            filters |= Q(ordnance_condition__icontains=term)

        ordering = (
            F(order_by).desc(nulls_last=True)
            if descending
            else F(order_by).asc(nulls_last=True)
        )
        queryset = UXORecord.objects.filter(filters).order_by(ordering)
        serializer = UXORecordSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(
    tags=["Search & Sort"],
    parameters=[
        OpenApiParameter(
            name="field",
            description="Exact field name to match (e.g., region, ordnance_type, ordnance_condition).",
            required=True,
            type=str,
        ),
        OpenApiParameter(
            name="value",
            description="Value to match exactly (case-insensitive).",
            required=True,
            type=str,
            examples=[
                OpenApiExample(
                    name="Single Search Term", value="Aleppo", parameter_only=True
                ),
                OpenApiExample(
                    name="Multiple Terms", value="Raqqa,Cluster", parameter_only=True
                ),
            ],
        ),
    ],
    responses=UXORecordSerializer(many=True),
)
class FieldMatchFilterView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        field = request.query_params.get("field")
        value = request.query_params.get("value")

        if not field or not value:
            return Response(
                {"error": "Both 'field' and 'value' query parameters are required."},
                status=400,
            )

        if not hasattr(UXORecord, field):
            return Response({"error": f"Invalid field: {field}"}, status=400)

        try:
            queryset = UXORecord.objects.filter(**{f"{field}__iexact": value})
            serializer = UXORecordSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
