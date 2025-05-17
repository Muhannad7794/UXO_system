from django.urls import path
from uxo_records.views import (
    UXORecordListCreateView,
    UXORecordRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("records/", UXORecordListCreateView.as_view(), name="uxo-records-list-create"),
    path(
        "records/<int:pk>/",
        UXORecordRetrieveUpdateDestroyView.as_view(),
        name="uxo-records-detail",
    ),
]
