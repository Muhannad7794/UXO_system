import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

from django.db.models import Avg, Count, Max, Min, Sum
from django.core.exceptions import FieldDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from ..utils import get_annotated_uxo_queryset, ANNOTATION_MAP
from uxo_records.models import UXORecord

# --- CONFIGURATION ---

AGGREGATION_MAP = {"avg": Avg, "max": Max, "min": Min, "sum": Sum, "count": Count}

VALID_GROUPING_FIELDS = [
    "region__name",
    "ordnance_type",
    "ordnance_condition",
    "is_loaded",
    "proximity_to_civilians",
    "burial_status",
]
# CORRECTED: Use 'longitude' and 'latitude' which are now annotated in utils.py
# This keeps the names consistent with the original dataset.
VALID_NUMERIC_FIELDS = ["danger_score", "longitude", "latitude"]
VALID_NUMERIC_FIELDS += list(ANNOTATION_MAP.keys())


def _get_label_maps(field_name):
    """
    Helper function to get the human-readable labels for a given model field
    that has 'choices' defined.
    """
    try:
        # For annotated fields, ANNOTATION_MAP form utils.py is used.
        if field_name in ANNOTATION_MAP:
            source_field_name, numeric_map = ANNOTATION_MAP[field_name]
            # Get the choices from the original model field
            choices = dict(UXORecord._meta.get_field(source_field_name).choices)
            # Map the choice CODE to the full LABEL
            # Then map the numeric value to that full LABEL
            code_to_label_map = {str(k): v for k, v in choices.items()}
            value_to_code_map = {str(float(v)): k for k, v in numeric_map.items()}
            return {
                num_val: code_to_label_map.get(code)
                for num_val, code in value_to_code_map.items()
            }

        # This will now correctly fail to find 'longitude' or 'latitude' as a real field
        # and the except block will handle it gracefully.
        field = UXORecord._meta.get_field(field_name.replace("__name", ""))
        if field.choices:
            return dict(field.choices)
    except (AttributeError, KeyError, FieldDoesNotExist):
        return None
    return None


@extend_schema(
    summary="Generate Advanced UXO Statistics",
    description="""
A flexible endpoint to generate various statistics. Supports `aggregate`, `grouped`, `bivariate`, `regression`, and `kmeans` analysis types.
    """,
    parameters=[
        OpenApiParameter(
            name="analysis_type",
            required=True,
            type=str,
            enum=["aggregate", "grouped", "bivariate", "regression", "kmeans"],
        ),
        OpenApiParameter(
            name="numeric_field",
            type=str,
            description="Field for 'aggregate' analysis (e.g., 'danger_score').",
        ),
        OpenApiParameter(
            name="operation",
            type=str,
            description="Operation for 'aggregate' analysis (e.g., 'avg').",
        ),
        OpenApiParameter(
            name="group_by",
            type=str,
            description="Field to group by for 'grouped' analysis.",
        ),
        OpenApiParameter(
            name="aggregate_op",
            type=str,
            description="Aggregation function for groups. Defaults to 'count'.",
        ),
        OpenApiParameter(
            name="aggregate_field",
            type=str,
            description="Field for aggregation within groups.",
        ),
        OpenApiParameter(
            name="x_field",
            type=str,
            description="Field for X-axis (bivariate/regression). e.g. longitude",
        ),
        OpenApiParameter(
            name="y_field",
            type=str,
            description="Field for Y-axis (bivariate/regression). e.g. latitude",
        ),
        OpenApiParameter(
            name="k", type=int, description="Number of clusters for K-Means analysis."
        ),
        OpenApiParameter(
            name="features",
            type=str,
            description="Comma-separated numeric fields for K-Means clustering.",
        ),
    ],
    tags=["Reports & Analytics"],
)
class StatisticsView(APIView):
    """A consolidated view to handle various statistical analyses using an annotated queryset."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """The base for all queries is now the annotated queryset from utils."""
        return get_annotated_uxo_queryset()

    def get(self, request, *args, **kwargs):
        analysis_type = request.query_params.get("analysis_type")

        label_maps = {}
        if analysis_type == "grouped":
            group_by_field = request.query_params.get("group_by")
            label_maps["group"] = _get_label_maps(group_by_field)
        elif analysis_type in ["bivariate", "regression"]:
            x_field = request.query_params.get("x_field")
            y_field = request.query_params.get("y_field")
            label_maps["x_axis"] = _get_label_maps(x_field)
            label_maps["y_axis"] = _get_label_maps(y_field)
        elif analysis_type == "kmeans":
            # Add logic to get maps for K-Means features ---
            features_str = request.query_params.get("features", "")
            if features_str:
                features = features_str.split(",")
                for feature in features:
                    feature_map = _get_label_maps(feature)
                    if feature_map:
                        label_maps[feature] = feature_map

        # Dispatch the request to the correct analysis method
        analysis_method_map = {
            "aggregate": self.perform_aggregate_analysis,
            "grouped": self.perform_grouped_analysis,
            "bivariate": self.perform_bivariate_analysis,
            "regression": self.perform_regression_analysis,
            "kmeans": self.perform_kmeans_analysis,
        }

        analysis_method = analysis_method_map.get(analysis_type)

        if not analysis_method:
            return Response(
                {"error": "Invalid or missing 'analysis_type' parameter."}, status=400
            )

        response = analysis_method(request)

        # Inject label maps into successful responses
        if response.status_code == 200 and isinstance(response.data, dict):
            non_empty_maps = {k: v for k, v in label_maps.items() if v}
            if non_empty_maps:
                response.data["label_maps"] = non_empty_maps

        return response

    def _validate_params(self, params, required_fields, valid_fields_map={}):
        """Helper function to validate query parameters."""
        for field in required_fields:
            if not params.get(field):
                return f"'{field}' is required for this analysis type."

        for field, valid_values in valid_fields_map.items():
            param_value = params.get(field)
            if param_value and param_value not in valid_values:
                return f"Unsupported value for '{field}'. Valid options are: {', '.join(valid_values)}"
        return None

    # --- Aggregate Analysis ---
    def perform_aggregate_analysis(self, request):
        params = request.query_params
        error = self._validate_params(
            params,
            ["numeric_field", "operation"],
            {"numeric_field": VALID_NUMERIC_FIELDS},
        )
        if error:
            return Response({"error": error}, status=400)

        field, op_str = params.get("numeric_field"), params.get("operation")
        op_func = AGGREGATION_MAP.get(op_str)
        if not op_func:
            return Response(
                {"error": f"Unsupported operation: '{op_str}'."}, status=400
            )

        queryset = self.get_queryset()
        agg_arg = "id" if op_str == "count" else field
        result = queryset.aggregate(result=op_func(agg_arg))
        return Response(
            {
                "analysis_type": "aggregate",
                "parameters": params,
                "result": result.get("result"),
            }
        )

    # --- Grouped Analysis ---
    def perform_grouped_analysis(self, request):
        params = request.query_params
        error = self._validate_params(
            params, ["group_by"], {"group_by": VALID_GROUPING_FIELDS}
        )
        if error:
            return Response({"error": error}, status=400)
        group_by = params.get("group_by")
        agg_op_str = params.get("aggregate_op", "count")
        agg_field = params.get("aggregate_field")
        if agg_op_str != "count" and not agg_field:
            return Response(
                {
                    "error": f"'aggregate_field' is required when 'aggregate_op' is '{agg_op_str}'."
                },
                status=400,
            )
        if agg_field and agg_field not in VALID_NUMERIC_FIELDS:
            return Response(
                {"error": f"Aggregation on field '{agg_field}' is not supported."},
                status=400,
            )
        op_func = AGGREGATION_MAP.get(agg_op_str)
        if not op_func:
            return Response(
                {"error": f"Unsupported operation: '{agg_op_str}'."}, status=400
            )
        queryset = self.get_queryset().values(group_by)
        annotation_arg = "id" if agg_op_str == "count" else agg_field
        annotation = queryset.annotate(result=op_func(annotation_arg)).order_by(
            "-result"
        )
        results_list = [
            {"group": item[group_by], "value": item["result"]} for item in annotation
        ]
        return Response(
            {"analysis_type": "grouped", "parameters": params, "results": results_list}
        )

    # --- Bivariate Analysis ---
    def perform_bivariate_analysis(self, request):
        params = request.query_params
        error = self._validate_params(
            params,
            ["x_field", "y_field"],
            {"x_field": VALID_NUMERIC_FIELDS, "y_field": VALID_NUMERIC_FIELDS},
        )
        if error:
            return Response({"error": error}, status=400)
        x_field, y_field = params.get("x_field"), params.get("y_field")
        data = self.get_queryset().values_list(x_field, y_field)
        return Response(
            {"analysis_type": "bivariate", "parameters": params, "results": list(data)}
        )

    # --- Regression Analysis ---
    def perform_regression_analysis(self, request):
        params = request.query_params
        error = self._validate_params(
            params,
            ["x_field", "y_field"],
            {"x_field": VALID_NUMERIC_FIELDS, "y_field": VALID_NUMERIC_FIELDS},
        )
        if error:
            return Response({"error": error}, status=400)
        x_field, y_field = params.get("x_field"), params.get("y_field")
        queryset = self.get_queryset().values(x_field, y_field)
        df = pd.DataFrame.from_records(queryset).dropna()
        if len(df) < 2:
            return Response(
                {"error": "Not enough data points for regression analysis."}, status=400
            )
        X = df[[x_field]].values
        y = df[y_field].values
        model = LinearRegression()
        model.fit(X, y)
        response_data = {
            "analysis_type": "regression",
            "parameters": params,
            "statistics": {
                "r_squared": model.score(X, y),
                "slope": model.coef_[0],
                "intercept": model.intercept_,
                "variance": np.var(y),
                "mean_of_dependent_variable": np.mean(y),
            },
            "scatter_data": df.to_dict("records"),
        }
        return Response(response_data)

    # --- K-Means Clustering ---
    def perform_kmeans_analysis(self, request):
        params = request.query_params
        try:
            k = int(params.get("k"))
            features_str = params.get("features")
            if not k or not features_str:
                raise ValueError()
            features = features_str.split(",")
        except (ValueError, TypeError):
            return Response(
                {
                    "error": "Invalid or missing 'k' (integer) and 'features' (comma-separated string) parameters are required."
                },
                status=400,
            )

        for feature in features:
            if feature not in VALID_NUMERIC_FIELDS:
                return Response(
                    {
                        "error": f"Invalid feature '{feature}'. Please use fields from the valid numeric fields list."
                    },
                    status=400,
                )

        queryset = self.get_queryset().values(*features, "id")
        df = pd.DataFrame.from_records(queryset).dropna()

        if len(df) < k:
            return Response(
                {
                    "error": f"Cannot create {k} clusters with only {len(df)} data points."
                },
                status=400,
            )

        kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto")
        cluster_data = df[features]
        df["cluster"] = kmeans.fit_predict(cluster_data)
        response_data = {
            "analysis_type": "kmeans",
            "parameters": params,
            "results": df.to_dict("records"),
        }
        return Response(response_data)
