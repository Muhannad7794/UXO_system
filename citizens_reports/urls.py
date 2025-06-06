# citizens_reports/urls.py

from django.urls import path
from .views import (
    SubmitCitizenReportView,
    ListCitizenReportsView,
    RetrieveDeleteCitizenReportView,
    VerifyCitizenReportView,
)

urlpatterns = [
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
