"""用户模块的服务层。

当前服务层同时负责：
1. 登录校验；
2. 用户管理列表查询；
3. 用户新增、编辑、删除。
"""

from django.db.models import Q
from django.utils import timezone
from rest_framework import exceptions

from .models import ParkUser


ROLE_NAME_MAP = {
    "admin": "系统管理员",
    "operator": "值班管理员",
    "viewer": "只读用户",
}

STATUS_NAME_MAP = {
    1: ("启用", "free"),
    0: ("停用", "warning"),
}


def get_user_module_info():
    """返回模块说明信息，便于快速确认接口是否挂载成功。"""

    return {
        "module": "users",
        "description": "User and permission management module.",
    }


def _format_datetime(value):
    """统一格式化用户管理页中需要展示的时间字段。"""

    if value is None:
        return "--"
    return timezone.localtime(value).strftime("%Y-%m-%d %H:%M")


def _serialize_user(user: ParkUser) -> dict:
    """将用户模型转换为前端用户管理页所需结构。"""

    status_label, status_type = STATUS_NAME_MAP.get(user.status, ("异常", "warning"))
    return {
        "id": user.id,
        "username": user.username,
        "realName": user.real_name,
        "phone": user.phone or "--",
        "role": user.role,
        "roleName": ROLE_NAME_MAP.get(user.role, user.role),
        "status": status_label,
        "statusValue": user.status,
        "type": status_type,
        "lastLogin": _format_datetime(user.last_login),
        "createdAt": _format_datetime(user.created_at),
    }


def _get_user_or_raise(pk: int) -> ParkUser:
    """按主键获取用户，不存在时抛出 404。"""

    user = ParkUser.objects.filter(pk=pk).first()
    if user is None:
        raise exceptions.NotFound("用户不存在。")
    return user


def login_user(username, password):
    """校验数据库中的账号密码并返回前端登录所需信息。"""

    user = ParkUser.objects.filter(username=username, status=1).first()
    if user is None or user.password != password:
        raise exceptions.AuthenticationFailed("账号或密码不正确。")

    # 登录成功后顺手刷新最后登录时间，便于用户管理页展示真实痕迹。
    user.last_login = timezone.now()
    user.updated_at = timezone.now()
    user.save(update_fields=["last_login", "updated_at"])

    return {
        "id": user.id,
        "username": user.username,
        "displayName": user.real_name,
        "role": user.role,
        "roleName": ROLE_NAME_MAP.get(user.role, user.role),
        "token": f"token-{user.id}",
    }


def list_users(keyword="", status="", role=""):
    """按关键词、状态和角色筛选用户列表。"""

    queryset = ParkUser.objects.all().order_by("-created_at")
    normalized_keyword = keyword.strip()
    normalized_status = status.strip().lower()
    normalized_role = role.strip().lower()

    if normalized_keyword:
        queryset = queryset.filter(
            Q(username__icontains=normalized_keyword)
            | Q(real_name__icontains=normalized_keyword)
            | Q(phone__icontains=normalized_keyword)
        )

    if normalized_status == "free":
        queryset = queryset.filter(status=1)
    elif normalized_status == "warning":
        queryset = queryset.filter(status=0)
    elif normalized_status:
        queryset = queryset.none()

    if normalized_role:
        queryset = queryset.filter(role=normalized_role)

    return [_serialize_user(user) for user in queryset]


def create_user(validated_data: dict) -> dict:
    """创建新的系统用户。"""

    if ParkUser.objects.filter(username=validated_data["username"]).exists():
        raise exceptions.ValidationError({"username": ["登录账号已存在。"]})

    now = timezone.now()
    user = ParkUser.objects.create(
        username=validated_data["username"],
        password=validated_data["password"],
        real_name=validated_data["real_name"],
        phone=validated_data.get("phone") or None,
        role=validated_data["role"],
        status=validated_data["status"],
        created_at=now,
        updated_at=now,
    )
    return _serialize_user(user)


def update_user(pk: int, validated_data: dict) -> dict:
    """更新指定用户记录。"""

    user = _get_user_or_raise(pk)
    duplicate = ParkUser.objects.filter(username=validated_data["username"]).exclude(pk=pk).exists()
    if duplicate:
        raise exceptions.ValidationError({"username": ["登录账号已存在。"]})

    user.username = validated_data["username"]
    user.password = validated_data["password"]
    user.real_name = validated_data["real_name"]
    user.phone = validated_data.get("phone") or None
    user.role = validated_data["role"]
    user.status = validated_data["status"]
    user.updated_at = timezone.now()
    user.save(update_fields=["username", "password", "real_name", "phone", "role", "status", "updated_at"])
    return _serialize_user(user)


def delete_user(pk: int) -> None:
    """删除指定用户记录。"""

    user = _get_user_or_raise(pk)
    user.delete()
