# In uxo_backend/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from django.contrib.auth import views as auth_views
from . import views
from .views import DataImportView

# Import the specific url lists from your apps
from reports.urls import api_urlpatterns as reports_api_urls
from reports.urls import web_urlpatterns as reports_web_urls
from citizens_reports.urls import web_urlpatterns as citizens_web_urls
from citizens_reports.urls import api_urlpatterns as citizens_api_urls


urlpatterns = [
    # Admin and Auth
    path("admin/", admin.site.urls),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", views.logout_view, name="logout"),
    # --- WEB PAGE URLS ---
    path("", views.index, name="index"),
    path("", include(citizens_web_urls)),
    path("reports/", include(reports_web_urls)),  # To create /reports/statistics/
    path("data-import/", DataImportView.as_view(), name="data-import-page"),
    # --- API ENDPOINTS ---
    path("api/v1/records/", include("uxo_records.urls")),
    path(
        "api/v1/reports/", include(reports_api_urls)
    ),  # To create /api/v1/reports/statistics/
    path("api/v1/citizen-reports/", include(citizens_api_urls)),
    # --- Schema & Docs ---
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Media file serving for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
