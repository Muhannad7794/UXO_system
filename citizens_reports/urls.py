# citizens_reports/urls.py

from django.urls import path
from .views import (
    SubmitCitizenReportView,
    ListCitizenReportsView,
    RetrieveDeleteCitizenReportView,
    VerifyCitizenReportView,
    # web views
    CitizenReportFormView,
    PendingReportsListView,
    PendingReportDetailView,
    RejectReportView,
)

api_urlpatterns = [
    # Public endpoint for submitting a new report
    path("submit/", SubmitCitizenReportView.as_view(), name="submit-citizen-report"),
    # Admin endpoint to list all reports for review
    path("review/", ListCitizenReportsView.as_view(), name="list-citizen-reports"),
    # Admin endpoint to retrieve or delete a specific report
    path(
        "review/<int:pk>/",
        RetrieveDeleteCitizenReportView.as_view(),
        name="detail-citizen-report",
    ),
    # Admin endpoint that presents the form to verify a report
    path(
        "review/<int:pk>/verify/",
        VerifyCitizenReportView.as_view(),
        name="verify-citizen-report",
    ),
]

web_urlpatterns = [
    path(
        "submit-form/",
        CitizenReportFormView.as_view(),
        name="submit-citizen-report-form",
    ),
    path("review/", PendingReportsListView.as_view(), name="review-list"),
    path("review/<int:pk>/", PendingReportDetailView.as_view(), name="review-detail"),
    path("review/<int:pk>/reject/", RejectReportView.as_view(), name="reject-report"),
]

# Combine the url lists to be discoverable by Django
urlpatterns = web_urlpatterns + api_urlpatterns
