from django.urls import path

from .views import UserManageDetailView, UserManageView, UserModuleView

app_name = "users"

urlpatterns = [
    path("", UserModuleView.as_view(), name="index"),
    path("manage/", UserManageView.as_view(), name="manage"),
    path("manage/<int:pk>/", UserManageDetailView.as_view(), name="manage-detail"),
]
