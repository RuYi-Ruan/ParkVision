from django.urls import path

from .views import VehicleDetailView, VehicleModuleView

app_name = "vehicles"

urlpatterns = [
    path("", VehicleModuleView.as_view(), name="index"),
    path("<int:pk>/", VehicleDetailView.as_view(), name="detail"),
]
