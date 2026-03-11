from django.urls import path

from .views import ParkingModuleView

app_name = "parking"

urlpatterns = [
    path("", ParkingModuleView.as_view(), name="index"),
]
