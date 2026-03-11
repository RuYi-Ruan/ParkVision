from django.urls import path

from .views import DashboardModuleView

app_name = "dashboard"

urlpatterns = [
    path("", DashboardModuleView.as_view(), name="index"),
]
