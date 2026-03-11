from django.urls import path

from .views import VehicleModuleView

app_name = "vehicles"

urlpatterns = [
    path("", VehicleModuleView.as_view(), name="index"),
]
