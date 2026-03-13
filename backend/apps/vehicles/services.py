"""车辆模块的服务层。

这里统一封装车辆的查询、创建、更新、删除和详情聚合逻辑，
避免视图层直接操作模型，方便后续继续扩展到更完整的车辆档案。
"""

from django.db.models import Q
from django.utils import timezone
from rest_framework import exceptions

from apps.records.models import ParkingRecord
from apps.vehicles.models import Vehicle

VEHICLE_STATUS_TYPE_MAP = {
    1: ("已备案", "free"),
    0: ("停用", "warning"),
}

RECORD_STATUS_TYPE_MAP = {
    "在场": "busy",
    "已离场": "free",
    "异常": "warning",
}


def get_vehicle_module_info():
    """返回模块说明信息，便于接口联调时检查模块状态。"""
    return {
        "module": "vehicles",
        "description": "Vehicle information management module.",
    }


def _serialize_vehicle(vehicle: Vehicle) -> dict:
    """将车辆模型转换为车辆管理列表所需结构。"""
    status_label, status_type = VEHICLE_STATUS_TYPE_MAP.get(vehicle.status, ("异常", "warning"))
    return {
        "id": vehicle.id,
        "plate": vehicle.plate_number,
        "owner": vehicle.owner_name,
        "ownerPhone": vehicle.owner_phone or "",
        "category": vehicle.vehicle_type,
        "color": vehicle.color or "",
        "space": vehicle.remark or "--",
        "status": status_label,
        "statusValue": vehicle.status,
        "type": status_type,
    }


def _format_datetime(value):
    """统一格式化车辆详情里用到的时间字段。"""
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


def _serialize_recent_record(record: ParkingRecord) -> dict:
    """整理车辆详情页中的最近停车记录摘要。"""
    return {
        "id": record.id,
        "recordNo": record.record_no,
        "enterAt": _format_datetime(record.entry_time),
        "leaveAt": _format_datetime(record.exit_time),
        "duration": _format_duration(record),
        "status": record.record_status,
        "type": RECORD_STATUS_TYPE_MAP.get(record.record_status, "warning"),
        "amount": f"{record.amount:.2f}",
    }


def _get_vehicle_or_raise(pk: int) -> Vehicle:
    """按主键获取车辆，不存在时抛出 404。"""
    vehicle = Vehicle.objects.filter(pk=pk).first()
    if vehicle is None:
        raise exceptions.NotFound("车辆不存在")
    return vehicle


def list_vehicles(keyword="", status=""):
    """按关键词和状态筛选车辆列表。"""
    queryset = Vehicle.objects.all().order_by("plate_number")
    normalized_keyword = keyword.strip()
    normalized_status = status.strip().lower()

    if normalized_keyword:
        queryset = queryset.filter(
            Q(plate_number__icontains=normalized_keyword)
            | Q(owner_name__icontains=normalized_keyword)
            | Q(vehicle_type__icontains=normalized_keyword)
        )

    if normalized_status == "free":
        queryset = queryset.filter(status=1)
    elif normalized_status == "warning":
        queryset = queryset.filter(status=0)
    elif normalized_status:
        queryset = queryset.none()

    return [_serialize_vehicle(vehicle) for vehicle in queryset]


def get_vehicle_detail(pk: int) -> dict:
    """返回单辆车的档案详情与最近停车记录。"""
    vehicle = _get_vehicle_or_raise(pk)
    status_label, status_type = VEHICLE_STATUS_TYPE_MAP.get(vehicle.status, ("异常", "warning"))
    records = list(ParkingRecord.objects.filter(vehicle_id=vehicle.id).order_by("-entry_time")[:5])
    active_record = next((record for record in records if record.record_status == "在场"), None)

    return {
        "id": vehicle.id,
        "plate": vehicle.plate_number,
        "owner": vehicle.owner_name,
        "ownerPhone": vehicle.owner_phone or "--",
        "category": vehicle.vehicle_type,
        "color": vehicle.color or "--",
        "status": status_label,
        "type": status_type,
        "remark": vehicle.remark or "暂无备注",
        "createdAt": _format_datetime(vehicle.created_at),
        "updatedAt": _format_datetime(vehicle.updated_at),
        "currentRecordId": active_record.id if active_record else None,
        "recentRecords": [_serialize_recent_record(record) for record in records],
    }


def create_vehicle(validated_data: dict) -> dict:
    """创建一条新的车辆记录。"""
    if Vehicle.objects.filter(plate_number=validated_data["plate_number"]).exists():
        raise exceptions.ValidationError({"plate_number": ["车牌号已存在"]})

    now = timezone.now()
    vehicle = Vehicle.objects.create(
        plate_number=validated_data["plate_number"],
        owner_name=validated_data["owner_name"],
        owner_phone=validated_data.get("owner_phone") or None,
        vehicle_type=validated_data["vehicle_type"],
        color=validated_data.get("color") or None,
        status=validated_data["status"],
        remark=validated_data.get("remark") or None,
        created_at=now,
        updated_at=now,
    )
    return _serialize_vehicle(vehicle)


def update_vehicle(pk: int, validated_data: dict) -> dict:
    """更新指定车辆记录。"""
    vehicle = _get_vehicle_or_raise(pk)
    duplicate = Vehicle.objects.filter(plate_number=validated_data["plate_number"]).exclude(pk=pk).exists()
    if duplicate:
        raise exceptions.ValidationError({"plate_number": ["车牌号已存在"]})

    vehicle.plate_number = validated_data["plate_number"]
    vehicle.owner_name = validated_data["owner_name"]
    vehicle.owner_phone = validated_data.get("owner_phone") or None
    vehicle.vehicle_type = validated_data["vehicle_type"]
    vehicle.color = validated_data.get("color") or None
    vehicle.status = validated_data["status"]
    vehicle.remark = validated_data.get("remark") or None
    vehicle.updated_at = timezone.now()
    vehicle.save(
        update_fields=["plate_number", "owner_name", "owner_phone", "vehicle_type", "color", "status", "remark", "updated_at"]
    )
    return _serialize_vehicle(vehicle)


def delete_vehicle(pk: int) -> None:
    """删除指定车辆记录。"""
    vehicle = _get_vehicle_or_raise(pk)
    vehicle.delete()
