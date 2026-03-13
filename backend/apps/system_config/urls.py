from django.urls import path

from .views import SystemConfigView

app_name = "system_config"

urlpatterns = [
    path("", SystemConfigView.as_view(), name="index"),
]
