# reports/urls.py

from django.urls import path
from reports.views.statistics_views import AggregationView, GroupedCountView
from reports.views.quantity_filters_views import (
    TopNRecordsView,
    BottomNRecordsView,
    FilterByThresholdView,
)
from reports.views.search_sort_views import (
    CombinedSearchAndOrderingView,
    FieldMatchFilterView,
)
from reports.views.visualization_views import (
    HeatmapDataView,
    HistogramDataView,
    BarChartDataView,
    PieChartDataView,
)

urlpatterns = [
    # Statistics & Aggregation
    path("aggregate/", AggregationView.as_view(), name="aggregate-stats"),
    path("grouped-count/", GroupedCountView.as_view(), name="grouped-count"),
    # Quantity-based filters
    path("top-n/", TopNRecordsView.as_view(), name="top-n"),
    path("bottom-n/", BottomNRecordsView.as_view(), name="bottom-n"),
    path("threshold-filter/", FilterByThresholdView.as_view(), name="threshold-filter"),
    # Advanced search & sorting
    path(
        "combined-search/",
        CombinedSearchAndOrderingView.as_view(),
        name="combined-search",
    ),
    path("field-match/", FieldMatchFilterView.as_view(), name="field-match"),
    # Visualization endpoints
    path("visualization/heatmap/", HeatmapDataView.as_view(), name="heatmap-data"),
    path(
        "visualization/histogram/", HistogramDataView.as_view(), name="histogram-data"
    ),
    path("visualization/bar-chart/", BarChartDataView.as_view(), name="bar-chart-data"),
    path("visualization/pie-chart/", PieChartDataView.as_view(), name="pie-chart-data"),
]
