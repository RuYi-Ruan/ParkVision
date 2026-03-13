"""车位模块的接口视图。"""

from rest_framework.views import APIView

from common.permissions.access import ensure_authenticated, ensure_roles
from common.response import api_response

from .serializers import ParkingSpaceQuerySerializer, ParkingSpaceWriteSerializer
from .services import (
    create_parking_space,
    delete_parking_space,
    get_parking_module_info,
    get_parking_space_detail,
    list_parking_monitor,
    list_parking_spaces,
    update_parking_space,
)


class ParkingModuleView(APIView):
    """返回模块信息、车位列表以及新增车位能力。"""

    def get(self, request):
        ensure_authenticated(request)
        if request.query_params.get("mode") == "module":
            return api_response(get_parking_module_info())

        # 当前列表查询只需要关键词和状态两项核心条件。
        serializer = ParkingSpaceQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = list_parking_spaces(**serializer.validated_data)
        return api_response(data=data)

    def post(self, request):
        ensure_roles(request, "admin", "operator")
        serializer = ParkingSpaceWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = create_parking_space(serializer.validated_data)
        return api_response(data=data, message="create success")


class ParkingDetailView(APIView):
    """处理单条车位记录的详情、编辑与删除。"""

    def get(self, request, pk: int):
        ensure_authenticated(request)
        data = get_parking_space_detail(pk)
        return api_response(data=data)

    def put(self, request, pk: int):
        ensure_roles(request, "admin", "operator")
        serializer = ParkingSpaceWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = update_parking_space(pk, serializer.validated_data)
        return api_response(data=data, message="update success")

    def delete(self, request, pk: int):
        ensure_roles(request, "admin", "operator")
        delete_parking_space(pk)
        return api_response(message="delete success")


class ParkingMonitorView(APIView):
    """返回车位监控页面需要的区域占用概览。"""

    def get(self, request):
        ensure_authenticated(request)
        return api_response(data=list_parking_monitor())
