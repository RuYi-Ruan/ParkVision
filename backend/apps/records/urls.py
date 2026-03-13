from django.urls import path

from .views import (
    RecordDetailView,
    RecordEntryView,
    RecordExitView,
    RecordExportView,
    RecordModuleView,
    RecordSummaryView,
)

app_name = "records"

urlpatterns = [
    path("", RecordModuleView.as_view(), name="index"),
    path("summary/", RecordSummaryView.as_view(), name="summary"),
    path("export/", RecordExportView.as_view(), name="export"),
    path("entry/", RecordEntryView.as_view(), name="entry"),
    path("exit/", RecordExitView.as_view(), name="exit"),
    path("<int:pk>/", RecordDetailView.as_view(), name="detail"),
]
