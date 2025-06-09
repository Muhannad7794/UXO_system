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

urlpatterns = [
    # Admin and Auth
    path("admin/", admin.site.urls),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", views.logout_view, name="logout"),
    # Template Pages
    path("", views.index, name="index"),
    # This includes the /review/ URL we created
    path("", include("citizens_reports.urls")),
    # API Endpoints
    path("api/v1/records/", include("uxo_records.urls")),
    path("api/v1/reports/", include("reports.urls")),
    # This includes the /api/v1/citizen-reports/review/<pk>/verify/ URL
    path("api/v1/citizen-reports/", include("citizens_reports.urls")),
    # Schema & Docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
