"""系统设置模块的接口视图。"""

from rest_framework.views import APIView

from common.permissions.access import ensure_roles
from common.response import api_response

from .serializers import SystemConfigSerializer
from .services import load_system_config, save_system_config


class SystemConfigView(APIView):
    """读取和保存系统设置。"""

    def get(self, request):
        # 系统设置允许管理员和值班管理员查看，便于联调和运行维护。
        ensure_roles(request, "admin", "operator")
        return api_response(data=load_system_config())

    def put(self, request):
        # 修改配置只开放给管理员，避免运行参数被误改。
        ensure_roles(request, "admin")
        serializer = SystemConfigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = save_system_config(serializer.validated_data)
        return api_response(data=data, message="update success")
