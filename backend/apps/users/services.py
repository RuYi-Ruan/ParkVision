"""users 模块的服务层。

当前服务层直接查询 MySQL 中已经存在的业务表，视图层只负责调度。
"""

from rest_framework import exceptions

from .models import ParkUser

ROLE_NAME_MAP = {
    "admin": "系统管理员",
    "operator": "值班管理员",
    "viewer": "只读用户",
}


def get_user_module_info():
    """返回模块说明信息，便于快速确认接口是否挂载成功。"""
    return {
        "module": "users",
        "description": "User and permission management module.",
    }


def login_user(username, password):
    """校验数据库中的账号密码并返回前端登录所需信息。"""
    user = ParkUser.objects.filter(username=username, status=1).first()
    if user is None or user.password != password:
        raise exceptions.AuthenticationFailed("账号或密码不正确")

    return {
        # 前端头部区域当前直接显示 username，这里优先返回更适合展示的真实姓名。
        "username": user.real_name,
        "role_name": ROLE_NAME_MAP.get(user.role, user.role),
        # 这里暂时仍使用演示 token，后续接入 JWT 或 Session 时再替换。
        "token": f"token-{user.id}",
    }
