"""停车记录模块的接口视图。"""

from rest_framework.views import APIView

from common.permissions.access import ensure_authenticated, ensure_roles
from common.response import api_response

from .serializers import RecordEntrySerializer, RecordExitSerializer
from .services import (
    create_entry_record,
    export_records_csv,
    get_record_detail,
    get_record_module_info,
    get_record_summary,
    list_records,
    settle_exit_record,
)


class RecordModuleView(APIView):
    """返回停车记录模块说明或停车记录列表。"""

    def get(self, request):
        ensure_authenticated(request)
        if request.query_params.get("mode") == "module":
            return api_response(get_record_module_info())

        # 记录列表支持关键词、记录状态、支付状态和入场日期范围筛选。
        data = list_records(
            keyword=request.query_params.get("keyword", ""),
            status=request.query_params.get("status", ""),
            pay_status=request.query_params.get("payStatus", ""),
            date_from=request.query_params.get("dateFrom", ""),
            date_to=request.query_params.get("dateTo", ""),
        )
        return api_response(data=data)


class RecordDetailView(APIView):
    """返回单条停车记录详情。"""

    def get(self, request, pk: int):
        ensure_authenticated(request)
        data = get_record_detail(pk)
        return api_response(data=data)


class RecordSummaryView(APIView):
    """返回停车记录页面顶部的汇总统计。"""

    def get(self, request):
        ensure_authenticated(request)
        data = get_record_summary(
            keyword=request.query_params.get("keyword", ""),
            status=request.query_params.get("status", ""),
            pay_status=request.query_params.get("payStatus", ""),
            date_from=request.query_params.get("dateFrom", ""),
            date_to=request.query_params.get("dateTo", ""),
        )
        return api_response(data=data)


class RecordExportView(APIView):
    """按当前筛选条件导出停车记录。"""

    def get(self, request):
        ensure_roles(request, "admin", "operator")
        return export_records_csv(
            keyword=request.query_params.get("keyword", ""),
            status=request.query_params.get("status", ""),
            pay_status=request.query_params.get("payStatus", ""),
            date_from=request.query_params.get("dateFrom", ""),
            date_to=request.query_params.get("dateTo", ""),
        )


class RecordEntryView(APIView):
    """模拟车辆入场，创建停车记录并占用车位。"""

    def post(self, request):
        ensure_roles(request, "admin", "operator")
        serializer = RecordEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = create_entry_record(serializer.validated_data)
        return api_response(data=data, message="entry success")


class RecordExitView(APIView):
    """模拟车辆出场，结算费用并释放车位。"""

    def post(self, request):
        ensure_roles(request, "admin", "operator")
        serializer = RecordExitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = settle_exit_record(serializer.validated_data)
        return api_response(data=data, message="exit success")
