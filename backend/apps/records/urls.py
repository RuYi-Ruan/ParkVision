from django.urls import path

from .views import RecordDetailView, RecordModuleView

app_name = "records"

urlpatterns = [
    path("", RecordModuleView.as_view(), name="index"),
    path("<int:pk>/", RecordDetailView.as_view(), name="detail"),
]
