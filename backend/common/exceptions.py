"""全局异常处理。

这里负责把 DRF 默认的异常结构转换成项目统一的响应格式。
"""

from rest_framework import status
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """将 DRF 异常包装为统一的 code/message/data 结构。"""
    response = exception_handler(exc, context)
    if response is None:
        return response

    # DRF 可能返回 detail，也可能返回字段级错误字典。
    # 这里统一收敛为一个 message，减少前端分支判断。
    detail = response.data
    if isinstance(detail, dict) and "detail" in detail:
        message = detail["detail"]
    else:
        message = detail

    response.data = {
        "code": response.status_code,
        "message": message,
        "data": None,
    }
    return response


def custom_404(request, exception):
    """处理未匹配路由的 404 响应。"""
    from common.response import api_response

    return api_response(
        data=None,
        message="Not Found",
        code=status.HTTP_404_NOT_FOUND,
        status_code=status.HTTP_404_NOT_FOUND,
    )


def custom_500(request):
    """处理未捕获异常的 500 响应。"""
    from common.response import api_response

    return api_response(
        data=None,
        message="Internal Server Error",
        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
