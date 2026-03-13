from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("apps.users.urls")),
    path("api/vehicles/", include("apps.vehicles.urls")),
    path("api/parking/", include("apps.parking.urls")),
    path("api/records/", include("apps.records.urls")),
    path("api/detection/", include("apps.detection.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),
    path("api/system-config/", include("apps.system_config.urls")),
]
