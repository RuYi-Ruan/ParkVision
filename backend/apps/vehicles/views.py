from rest_framework.views import APIView

from common.response import api_response

from .services import get_vehicle_module_info


class VehicleModuleView(APIView):
    def get(self, request):
        return api_response(get_vehicle_module_info())

# Create your views here.
