"""vehicles 模块的接口视图。"""

from rest_framework.views import APIView

from common.response import api_response

from .serializers import VehicleQuerySerializer, VehicleWriteSerializer
from .services import create_vehicle, delete_vehicle, get_vehicle_module_info, list_vehicles, update_vehicle


class VehicleModuleView(APIView):
    """返回车辆模块信息、车辆列表以及新增车辆能力。"""

    def get(self, request):
        if request.query_params.get("mode") == "module":
            return api_response(get_vehicle_module_info())

        # 列表接口只依赖关键词和状态两个筛选条件。
        serializer = VehicleQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = list_vehicles(**serializer.validated_data)
        return api_response(data=data)

    def post(self, request):
        # 新增车辆时统一经过写入序列化器校验。
        serializer = VehicleWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = create_vehicle(serializer.validated_data)
        return api_response(data=data, message="create success")


class VehicleDetailView(APIView):
    """处理单条车辆记录的编辑与删除。"""

    def put(self, request, pk: int):
        serializer = VehicleWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = update_vehicle(pk, serializer.validated_data)
        return api_response(data=data, message="update success")

    def delete(self, request, pk: int):
        delete_vehicle(pk)
        return api_response(message="delete success")
