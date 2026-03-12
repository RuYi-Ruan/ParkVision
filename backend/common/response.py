"""统一返回格式工具。

项目当前所有接口都约定返回 code、message、data 三个字段，
这样前端在联调阶段就能按同一套结构处理结果。
"""

from rest_framework.response import Response


def api_response(data=None, message="success", code=0, status_code=200):
    """构造统一的响应体。"""
    return Response(
        {
            "code": code,
            "message": message,
            "data": data,
        },
        status=status_code,
    )
