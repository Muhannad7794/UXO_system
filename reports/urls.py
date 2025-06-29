# reports/urls.py

from django.urls import path
from .views.statistics_views import StatisticsView
from .views.geospatial_views import HeatmapView, RecordsWithinBboxView, HotZoneView
from .web_views import StatisticsPageView

api_urlpatterns = [
    # URL for the main statistics endpoint
    path("statistics/", StatisticsView.as_view(), name="statistics"),
    # URLs for the geospatial reporting endpoints
    path("geospatial/heatmap/", HeatmapView.as_view(), name="heatmap"),
    path(
        "geospatial/within-bbox/", RecordsWithinBboxView.as_view(), name="within-bbox"
    ),
    path("geospatial/hotzones/", HotZoneView.as_view(), name="hotzones"),
]

web_urlpatterns = [
    path("ui_statistics/", StatisticsPageView.as_view(), name="statistics-page"),
]
