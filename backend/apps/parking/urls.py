from django.urls import path

from .views import ParkingDetailView, ParkingModuleView, ParkingMonitorView

app_name = "parking"

urlpatterns = [
    path("", ParkingModuleView.as_view(), name="index"),
    path("<int:pk>/", ParkingDetailView.as_view(), name="detail"),
    path("monitor/", ParkingMonitorView.as_view(), name="monitor"),
]
