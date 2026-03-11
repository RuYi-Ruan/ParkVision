from django.urls import path

from .views import UserModuleView

app_name = "users"

urlpatterns = [
    path("", UserModuleView.as_view(), name="index"),
]
