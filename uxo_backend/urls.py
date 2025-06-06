# uxo_backend/urls.py (Corrected)

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # === Local apps paths - Each app now has its own unique namespace ===
    # All uxo_records URLs will be under /api/v1/records/
    path("api/v1/records/", include("uxo_records.urls")),
    # All reports URLs will be under /api/v1/reports/
    path("api/v1/reports/", include("reports.urls")),
    # All citizens_reports URLs will be under /api/v1/citizen-reports/
    path("api/v1/citizen-reports/", include("citizens_reports.urls")),
    # === Schema & Docs ===
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # The UI paths are fine as they are
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
