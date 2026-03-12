"""parking 模块的服务层。

车位列表、监控概览以及基础增删改都从数据库中动态处理。
"""

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import exceptions

from .models import ParkingSpace

STATUS_TYPE_MAP = {
    "空闲": "free",
    "占用": "busy",
    "维护": "warning",
}


def get_parking_module_info():
    """返回 parking 模块说明信息。"""
    return {
        "module": "parking",
        "description": "Parking space management module.",
    }


def _serialize_space(space: ParkingSpace) -> dict:
    """将车位模型转换为前端列表需要的结构。"""
    return {
        "id": space.id,
        "code": space.space_code,
        "zone": space.area_code,
        "spaceType": space.space_type,
        "status": space.status,
        "updatedAt": space.updated_at.strftime("%H:%M"),
        "type": STATUS_TYPE_MAP.get(space.status, "warning"),
        "floorNo": space.floor_no or "",
        "remark": space.remark or "",
    }


def _get_space_or_raise(pk: int) -> ParkingSpace:
    """按主键获取车位，不存在时抛出 404。"""
    space = ParkingSpace.objects.filter(pk=pk).first()
    if space is None:
        raise exceptions.NotFound("车位不存在")
    return space


def list_parking_spaces(keyword="", status=""):
    """按关键词和状态过滤数据库中的车位列表。"""
    queryset = ParkingSpace.objects.all().order_by("space_code")
    normalized_keyword = keyword.strip()
    normalized_status = status.strip().lower()

    if normalized_keyword:
        queryset = queryset.filter(
            Q(space_code__icontains=normalized_keyword)
            | Q(area_code__icontains=normalized_keyword)
            | Q(status__icontains=normalized_keyword)
        )

    if normalized_status:
        db_status = next((name for name, code in STATUS_TYPE_MAP.items() if code == normalized_status), None)
        queryset = queryset.filter(status=db_status) if db_status else queryset.none()

    return [_serialize_space(space) for space in queryset]


def create_parking_space(validated_data: dict) -> dict:
    """创建一条新的车位记录。"""
    if ParkingSpace.objects.filter(space_code=validated_data["space_code"]).exists():
        raise exceptions.ValidationError({"space_code": ["车位编号已存在"]})

    now = timezone.now()
    space = ParkingSpace.objects.create(
        space_code=validated_data["space_code"],
        area_code=validated_data["area_code"],
        space_type=validated_data["space_type"],
        status=validated_data["status"],
        floor_no=validated_data.get("floor_no") or None,
        remark=validated_data.get("remark") or None,
        created_at=now,
        updated_at=now,
    )
    return _serialize_space(space)


def update_parking_space(pk: int, validated_data: dict) -> dict:
    """更新指定车位记录。"""
    space = _get_space_or_raise(pk)
    duplicate = ParkingSpace.objects.filter(space_code=validated_data["space_code"]).exclude(pk=pk).exists()
    if duplicate:
        raise exceptions.ValidationError({"space_code": ["车位编号已存在"]})

    space.space_code = validated_data["space_code"]
    space.area_code = validated_data["area_code"]
    space.space_type = validated_data["space_type"]
    space.status = validated_data["status"]
    space.floor_no = validated_data.get("floor_no") or None
    space.remark = validated_data.get("remark") or None
    space.updated_at = timezone.now()
    space.save(update_fields=["space_code", "area_code", "space_type", "status", "floor_no", "remark", "updated_at"])
    return _serialize_space(space)


def delete_parking_space(pk: int) -> None:
    """删除指定车位记录。"""
    space = _get_space_or_raise(pk)
    space.delete()


def list_parking_monitor():
    """按区域汇总监控卡片数据。"""
    grouped_spaces = (
        ParkingSpace.objects.values("area_code")
        .annotate(total=Count("id"), busy=Count("id", filter=Q(status="占用")))
        .order_by("area_code")
    )

    monitor_cards = []
    for index, item in enumerate(grouped_spaces, start=1):
        total = item["total"] or 0
        busy = item["busy"] or 0
        rate = "0%" if total == 0 else f"{round((busy / total) * 100)}%"
        monitor_cards.append(
            {
                "name": f"{item['area_code']}视角",
                "camera": f"CAM-{index:02d}",
                "rate": rate,
            }
        )

    return monitor_cards
