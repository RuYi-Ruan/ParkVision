"""dashboard 模块的接口视图。"""

from rest_framework.views import APIView

from common.permissions.access import ensure_authenticated
from common.response import api_response

from .services import get_dashboard_module_info, get_dashboard_overview


class DashboardModuleView(APIView):
    """返回模块信息或首页统计数据。"""

    def get(self, request):
        ensure_authenticated(request)

        # mode=module 用于检查模块状态；默认分支才是首页真实消费的数据。
        if request.query_params.get("mode") == "module":
            return api_response(get_dashboard_module_info())
        return api_response(get_dashboard_overview())
