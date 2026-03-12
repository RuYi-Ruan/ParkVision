"""records 模块的服务层。

停车记录列表和详情页都从数据库读取，服务层负责完成字段格式化和结构转换。
"""

from django.db.models import Q
from django.utils import timezone
from rest_framework import exceptions

from apps.records.models import ParkingRecord

RECORD_STATUS_TYPE_MAP = {
    "在场": "busy",
    "已离场": "free",
    "异常": "warning",
}


def get_record_module_info():
    """返回模块说明信息。"""
    return {
        "module": "records",
        "description": "Parking record management module.",
    }


def _format_datetime(value):
    """将时间格式化为前端更易读的文本。"""
    if value is None:
        return "--"
    return timezone.localtime(value).strftime("%Y-%m-%d %H:%M")


def _format_duration(record: ParkingRecord) -> str:
    """将停车分钟数格式化为中文可读文本。"""
    if record.record_status == "在场" or not record.duration_minutes:
        return "进行中"

    hours, minutes = divmod(record.duration_minutes, 60)
    if hours > 0 and minutes > 0:
        return f"{hours} 小时 {minutes} 分钟"
    if hours > 0:
        return f"{hours} 小时"
    return f"{minutes} 分钟"


def _serialize_record(record: ParkingRecord) -> dict:
    """将停车记录模型转换为前端列表所需结构。"""
    return {
        "id": record.id,
        "recordNo": record.record_no,
        "plate": record.plate_number,
        "enterAt": _format_datetime(record.entry_time),
        "leaveAt": _format_datetime(record.exit_time),
        "duration": _format_duration(record),
        "status": record.record_status,
        "type": RECORD_STATUS_TYPE_MAP.get(record.record_status, "warning"),
    }


def _serialize_record_detail(record: ParkingRecord) -> dict:
    """将单条停车记录转换为详情页所需结构。"""
    return {
        "id": record.id,
        "recordNo": record.record_no,
        "plate": record.plate_number,
        "entryGate": record.entry_gate or "--",
        "exitGate": record.exit_gate or "--",
        "enterAt": _format_datetime(record.entry_time),
        "leaveAt": _format_datetime(record.exit_time),
        "duration": _format_duration(record),
        "amount": f"{record.amount:.2f}",
        "payStatus": record.pay_status,
        "status": record.record_status,
        "remark": record.remark or "暂无备注",
        "entryImage": record.entry_image or "",
        "exitImage": record.exit_image or "",
    }


def _get_record_or_raise(pk: int) -> ParkingRecord:
    """按主键获取停车记录，不存在时抛出 404。"""
    record = ParkingRecord.objects.filter(pk=pk).first()
    if record is None:
        raise exceptions.NotFound("停车记录不存在")
    return record


def list_records(keyword="", status=""):
    """按关键词和状态过滤停车记录。"""
    queryset = ParkingRecord.objects.all().order_by("-entry_time")
    normalized_keyword = keyword.strip()
    normalized_status = status.strip().lower()

    if normalized_keyword:
        queryset = queryset.filter(
            Q(plate_number__icontains=normalized_keyword)
            | Q(record_status__icontains=normalized_keyword)
            | Q(record_no__icontains=normalized_keyword)
        )

    if normalized_status == "busy":
        queryset = queryset.filter(record_status="在场")
    elif normalized_status == "free":
        queryset = queryset.filter(record_status="已离场")
    elif normalized_status == "warning":
        queryset = queryset.filter(record_status="异常")
    elif normalized_status:
        queryset = queryset.none()

    return [_serialize_record(record) for record in queryset]


def get_record_detail(pk: int) -> dict:
    """获取单条停车记录的详情数据。"""
    record = _get_record_or_raise(pk)
    return _serialize_record_detail(record)
