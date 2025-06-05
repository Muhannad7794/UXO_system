# reports/urls.py

from django.urls import path
from .views import (
    statistics_views,
    geospatial_views,
)  # Assuming views are in these files

# We will create/update these views in the next steps
urlpatterns = [
    # A single, powerful endpoint for all statistical queries.
    # It will accept query parameters to define the analysis.
    # e.g., /api/v1/reports/statistics/?group_by=ordnance_type&aggregate=danger_score__avg
    path(
        "statistics/",
        statistics_views.StatisticsView.as_view(),
        name="report-statistics",
    ),
    # An endpoint to generate data suitable for a heatmap visualization.
    # It will return a list of coordinates and their weights (e.g., danger_score).
    path(
        "geospatial/heatmap/",
        geospatial_views.HeatmapView.as_view(),
        name="report-heatmap",
    ),
    # An endpoint to find all UXO records within a specified rectangular area (bounding box).
    # e.g., /api/v1/reports/geospatial/within-bbox/?bbox=35.0,33.0,37.0,34.0
    path(
        "geospatial/within-bbox/",
        geospatial_views.RecordsWithinBboxView.as_view(),
        name="report-records-within-bbox",
    ),
]
