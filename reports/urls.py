# reports/urls.py

from django.urls import path
from .views.statistics_views import StatisticsView
from .views.geospatial_views import HeatmapView, RecordsWithinBboxView, HotZoneView

urlpatterns = [
    # URL for the main statistics endpoint
    path("statistics/", StatisticsView.as_view(), name="statistics"),
    # URLs for the geospatial reporting endpoints
    path("geospatial/heatmap/", HeatmapView.as_view(), name="heatmap"),
    path(
        "geospatial/within-bbox/", RecordsWithinBboxView.as_view(), name="within-bbox"
    ),
    path("geospatial/hotzones/", HotZoneView.as_view(), name="hotzones"),
]
