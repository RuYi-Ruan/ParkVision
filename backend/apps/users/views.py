"""users 模块的接口视图。"""

from rest_framework.views import APIView

from common.response import api_response

from .serializers import UserLoginSerializer
from .services import get_user_module_info, login_user


class UserModuleView(APIView):
    """同时提供模块信息查询和登录接口。"""

    def get(self, request):
        # GET 主要用于开发阶段确认 users 模块已经正确挂载。
        return api_response(get_user_module_info())

    def post(self, request):
        # 参数校验交给序列化器，具体登录逻辑由服务层负责。
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = login_user(**serializer.validated_data)
        return api_response(data=data, message="login success")
