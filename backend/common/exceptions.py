from rest_framework import status
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

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
    from common.response import api_response

    return api_response(
        data=None,
        message="Not Found",
        code=status.HTTP_404_NOT_FOUND,
        status_code=status.HTTP_404_NOT_FOUND,
    )


def custom_500(request):
    from common.response import api_response

    return api_response(
        data=None,
        message="Internal Server Error",
        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
