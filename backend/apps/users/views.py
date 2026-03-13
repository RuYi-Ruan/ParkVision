"""用户模块的接口视图。"""

from rest_framework.views import APIView

from common.permissions.access import ensure_roles
from common.response import api_response

from .serializers import UserLoginSerializer, UserQuerySerializer, UserWriteSerializer
from .services import create_user, delete_user, get_user_module_info, list_users, login_user, update_user


class UserModuleView(APIView):
    """提供模块信息查询和登录接口。"""

    def get(self, request):
        # GET 主要用于开发阶段确认 users 模块已经正确挂载。
        return api_response(get_user_module_info())

    def post(self, request):
        # 登录参数校验交给序列化器，具体登录逻辑由服务层负责。
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = login_user(**serializer.validated_data)
        return api_response(data=data, message="login success")


class UserManageView(APIView):
    """处理用户管理列表查询和新增用户。"""

    def get(self, request):
        ensure_roles(request, "admin")
        serializer = UserQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = list_users(**serializer.validated_data)
        return api_response(data=data)

    def post(self, request):
        ensure_roles(request, "admin")
        serializer = UserWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = create_user(serializer.validated_data)
        return api_response(data=data, message="create success")


class UserManageDetailView(APIView):
    """处理单条用户记录的编辑与删除。"""

    def put(self, request, pk: int):
        ensure_roles(request, "admin")
        serializer = UserWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = update_user(pk, serializer.validated_data)
        return api_response(data=data, message="update success")

    def delete(self, request, pk: int):
        ensure_roles(request, "admin")
        delete_user(pk)
        return api_response(message="delete success")
