from django.urls import path
from .views import (
    SubmitCitizenReportView,
    ListAllCitizenReportsView,
    RetrieveCitizenReportByIdView,
    DeleteCitizenReportView,
    VerifyCitizenReportView,
)

urlpatterns = [
    path("submit/", SubmitCitizenReportView.as_view(), name="submit-citizen-report"),
    # Get
    path(
        "review/all/", ListAllCitizenReportsView.as_view(), name="list-citizen-reports"
    ),
    path(
        "review/<int:pk>/",
        RetrieveCitizenReportByIdView.as_view(),
        name="get-citizen-report",
    ),
    # Edit
    path(
        "review/<int:pk>/verify/",
        VerifyCitizenReportView.as_view(),
        name="verify-citizen-report",
    ),
    # Delete
    path(
        "review/<int:pk>/delete/",
        DeleteCitizenReportView.as_view(),
        name="delete-citizen-report",
    ),
]
