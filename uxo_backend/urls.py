# uxo_backend/urls.py (Corrected)

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # === Admin path ===
    path("admin/", admin.site.urls),
    ## login path
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    ## logout path
    path("logout/", views.logout_view, name="logout"),
    
    # === Local apps paths ===
    ## uxo_records URLs are under /api/v1/records/
    path("api/v1/records/", include("uxo_records.urls")),
    ## reports URLs are under /api/v1/reports/
    path("api/v1/reports/", include("reports.urls")),
    ## citizens_reports URLs are under /api/v1/citizen-reports/
    path("api/v1/citizen-reports/", include("citizens_reports.urls")),
    # === Templates paths ===
    path("", views.index, name="index"),
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
