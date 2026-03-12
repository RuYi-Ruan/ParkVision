"""records 模块的接口视图。"""

from rest_framework.views import APIView

from common.response import api_response

from .services import get_record_detail, get_record_module_info, list_records


class RecordModuleView(APIView):
    """返回停车记录模块信息或停车记录列表。"""

    def get(self, request):
        if request.query_params.get("mode") == "module":
            return api_response(get_record_module_info())

        # 停车记录页当前使用关键词和状态做基础筛选。
        data = list_records(
            keyword=request.query_params.get("keyword", ""),
            status=request.query_params.get("status", ""),
        )
        return api_response(data=data)


class RecordDetailView(APIView):
    """返回单条停车记录详情。"""

    def get(self, request, pk: int):
        data = get_record_detail(pk)
        return api_response(data=data)
