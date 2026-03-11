from django.urls import path

from .views import DetectionModuleView

app_name = "detection"

urlpatterns = [
    path("", DetectionModuleView.as_view(), name="index"),
]
