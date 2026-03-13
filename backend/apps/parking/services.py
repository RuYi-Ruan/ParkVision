"""车位模块的服务层。

车位列表、监控概览、详情聚合和基础增删改都从数据库动态处理，
后续接入识别结果时可以直接复用这里的结构。
"""

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import exceptions

from apps.records.models import ParkingRecord

from .models import ParkingSpace

STATUS_TYPE_MAP = {
    "空闲": "free",
    "占用": "busy",
    "维护": "warning",
}

RECORD_STATUS_TYPE_MAP = {
    "在场": "busy",
    "已离场": "free",
    "异常": "warning",
}


def get_parking_module_info():
    """返回 parking 模块说明信息。"""
    return {
        "module": "parking",
        "description": "Parking space management module.",
    }


def _format_datetime(value):
    """统一格式化车位详情中用到的时间字段。"""
    if value is None:
        return "--"
    return timezone.localtime(value).strftime("%Y-%m-%d %H:%M")


def _format_duration(record: ParkingRecord) -> str:
    """将停车时长格式化为中文可读文本。"""
    if record.record_status == "在场" or not record.duration_minutes:
        return "进行中"

    hours, minutes = divmod(record.duration_minutes, 60)
    if hours > 0 and minutes > 0:
        return f"{hours} 小时 {minutes} 分钟"
    if hours > 0:
        return f"{hours} 小时"
    return f"{minutes} 分钟"


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


def _serialize_space_record(record: ParkingRecord) -> dict:
    """整理车位详情页中的最近停车记录摘要。"""
    return {
        "id": record.id,
        "recordNo": record.record_no,
        "plate": record.plate_number,
        "enterAt": _format_datetime(record.entry_time),
        "leaveAt": _format_datetime(record.exit_time),
        "duration": _format_duration(record),
        "status": record.record_status,
        "type": RECORD_STATUS_TYPE_MAP.get(record.record_status, "warning"),
        "amount": f"{record.amount:.2f}",
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


def get_parking_space_detail(pk: int) -> dict:
    """返回单个车位的档案详情与最近停车记录。"""
    space = _get_space_or_raise(pk)
    records = list(ParkingRecord.objects.filter(space_id=space.id).order_by("-entry_time")[:5])
    active_record = next((record for record in records if record.record_status == "在场"), None)

    return {
        "id": space.id,
        "code": space.space_code,
        "zone": space.area_code,
        "spaceType": space.space_type,
        "status": space.status,
        "type": STATUS_TYPE_MAP.get(space.status, "warning"),
        "floorNo": space.floor_no or "--",
        "remark": space.remark or "暂无备注",
        "createdAt": _format_datetime(space.created_at),
        "updatedAt": _format_datetime(space.updated_at),
        "currentPlate": active_record.plate_number if active_record else "--",
        "currentRecordId": active_record.id if active_record else None,
        "recentRecords": [_serialize_space_record(record) for record in records],
    }


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
