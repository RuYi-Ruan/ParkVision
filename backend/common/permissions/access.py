"""轻量权限控制工具。

当前项目还没有接入 Django 原生认证体系，因此这里先基于演示 token
实现一层足够稳定的请求用户解析与角色校验能力，满足毕业设计阶段的
页面访问控制和关键写操作保护。
"""

from __future__ import annotations

import re

from rest_framework import exceptions

from apps.users.models import ParkUser


TOKEN_PATTERN = re.compile(r"^token-(?P<user_id>\d+)$")


def get_request_user(request) -> ParkUser:
    """根据请求头中的 token 解析当前登录用户。

    前端当前统一通过 `Authorization: Bearer token-用户ID` 的格式携带登录态。
    这里只做最小但真实的身份恢复，便于后续平滑切换到正式认证方案。
    """

    cached_user = getattr(request, "_park_user", None)
    if cached_user is not None:
        return cached_user

    raw_authorization = request.headers.get("Authorization", "").strip()
    if not raw_authorization:
        raise exceptions.NotAuthenticated("请先登录后再访问该接口。")

    token = raw_authorization
    if raw_authorization.lower().startswith("bearer "):
        token = raw_authorization.split(" ", 1)[1].strip()

    matched = TOKEN_PATTERN.match(token)
    if matched is None:
        raise exceptions.AuthenticationFailed("登录凭证格式无效，请重新登录。")

    user_id = int(matched.group("user_id"))
    user = ParkUser.objects.filter(pk=user_id, status=1).first()
    if user is None:
        raise exceptions.AuthenticationFailed("当前登录状态已失效，请重新登录。")

    request._park_user = user
    return user


def ensure_authenticated(request) -> ParkUser:
    """确保当前请求已经登录，并返回当前用户对象。"""

    return get_request_user(request)


def ensure_roles(request, *allowed_roles: str) -> ParkUser:
    """确保当前用户属于允许访问的角色集合。"""

    user = get_request_user(request)
    if user.role not in allowed_roles:
        raise exceptions.PermissionDenied("当前账号没有执行该操作的权限。")
    return user
