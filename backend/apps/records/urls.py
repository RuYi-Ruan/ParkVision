from django.urls import path

from .views import RecordModuleView

app_name = "records"

urlpatterns = [
    path("", RecordModuleView.as_view(), name="index"),
]
