from rest_framework.views import APIView

from common.response import api_response

from .services import get_detection_module_info


class DetectionModuleView(APIView):
    def get(self, request):
        return api_response(get_detection_module_info())

# Create your views here.
