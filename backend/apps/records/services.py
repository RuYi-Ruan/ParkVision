"""停车记录模块的服务层。

当前模块承担三类职责：
1. 从数据库读取停车记录列表与详情；
2. 按系统设置动态计算时长、费用和超时状态；
3. 提供模拟入场、模拟出场这类业务写入能力。
"""

from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal, ROUND_CEILING
from io import StringIO

from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import exceptions

from apps.parking.models import ParkingSpace
from apps.records.models import ParkingRecord
from apps.system_config.services import get_runtime_config
from apps.vehicles.models import Vehicle


DECIMAL_ZERO = Decimal("0.00")


def get_record_module_info():
    """返回停车记录模块说明信息。"""

    return {
        "module": "records",
        "description": "停车记录管理模块。",
    }


def _format_datetime(value):
    """将时间格式化为前端更易读的文本。"""

    if value is None:
        return "--"
    return timezone.localtime(value).strftime("%Y-%m-%d %H:%M")


def _generate_record_no() -> str:
    """生成停车记录编号，避免与现有记录冲突。"""

    while True:
        record_no = timezone.now().strftime("REC%Y%m%d%H%M%S%f")
        if not ParkingRecord.objects.filter(record_no=record_no).exists():
            return record_no


def _get_or_create_vehicle_by_plate(plate_number: str) -> Vehicle:
    """按车牌获取车辆，不存在时创建临时车辆档案。"""

    vehicle = Vehicle.objects.filter(plate_number=plate_number).first()
    if vehicle is not None:
        return vehicle

    now = timezone.now()
    return Vehicle.objects.create(
        plate_number=plate_number,
        owner_name="临时车辆",
        owner_phone=None,
        vehicle_type="小型车",
        color=None,
        user_id=None,
        status=1,
        remark="由停车记录模块自动创建",
        created_at=now,
        updated_at=now,
    )


def _get_space_or_raise(space_id: int) -> ParkingSpace:
    """按主键获取车位，不存在时抛出 404。"""

    space = ParkingSpace.objects.filter(pk=space_id).first()
    if space is None:
        raise exceptions.NotFound("车位不存在。")
    return space


def _get_available_space(space_id: int | None = None) -> ParkingSpace:
    """获取可用于入场的车位，支持优先指定车位。"""

    if space_id:
        space = _get_space_or_raise(space_id)
        if space.status != "空闲":
            raise exceptions.ValidationError({"space_id": ["所选车位当前不可用于入场。"]})
        return space

    fallback_space = ParkingSpace.objects.filter(status="空闲").order_by("space_code").first()
    if fallback_space is None:
        raise exceptions.ValidationError("当前没有可分配的空闲车位。")
    return fallback_space


def _get_active_record_by_plate(plate_number: str) -> ParkingRecord | None:
    """获取某车牌当前在场的停车记录。"""

    return (
        ParkingRecord.objects.filter(plate_number=plate_number, record_status="在场")
        .order_by("-entry_time")
        .first()
    )


def _normalize_record_minutes(record: ParkingRecord) -> int:
    """优先使用真实时间差计算停车分钟数，缺失时回退到数据库字段。"""

    end_time = record.exit_time or timezone.now()
    duration_seconds = max((end_time - record.entry_time).total_seconds(), 0)
    calculated_minutes = int(duration_seconds // 60)
    return calculated_minutes or max(record.duration_minutes or 0, 0)


def _resolve_record_pricing(record: ParkingRecord, parking_rule: dict) -> tuple[int, Decimal]:
    """根据系统设置中的收费规则计算停车分钟数和费用。"""

    duration_minutes = _normalize_record_minutes(record)
    free_minutes = max(int(parking_rule.get("free_minutes", 0) or 0), 0)
    fee_per_hour = Decimal(str(parking_rule.get("fee_per_hour", "0") or "0"))
    daily_cap = Decimal(str(parking_rule.get("daily_cap", "0") or "0"))

    if duration_minutes <= free_minutes:
        return duration_minutes, DECIMAL_ZERO

    chargeable_minutes = duration_minutes - free_minutes
    chargeable_hours = (Decimal(chargeable_minutes) / Decimal(60)).quantize(
        Decimal("1"),
        rounding=ROUND_CEILING,
    )
    amount = chargeable_hours * fee_per_hour

    if daily_cap > DECIMAL_ZERO:
        amount = min(amount, daily_cap)

    return duration_minutes, amount.quantize(Decimal("0.01"))


def _format_duration(duration_minutes: int, is_active: bool) -> str:
    """将停车分钟数转换为页面可读的中文文本。"""

    if is_active and duration_minutes <= 0:
        return "进行中"

    if duration_minutes <= 0:
        return "0 分钟"

    hours, minutes = divmod(duration_minutes, 60)
    if hours > 0 and minutes > 0:
        return f"{hours} 小时 {minutes} 分钟"
    if hours > 0:
        return f"{hours} 小时"
    return f"{minutes} 分钟"


def _resolve_display_status(record: ParkingRecord, duration_minutes: int, parking_rule: dict) -> tuple[str, str]:
    """根据记录状态和超时规则生成前端展示状态。"""

    if record.record_status == "异常":
        return "异常", "warning"

    overdue_hours = max(int(parking_rule.get("overdue_hours", 0) or 0), 0)
    overdue_minutes = overdue_hours * 60

    if record.record_status == "在场":
        if overdue_minutes > 0 and duration_minutes > overdue_minutes:
            return "超时在场", "warning"
        return "在场", "busy"

    if record.record_status == "已离场":
        return "已离场", "free"

    return record.record_status, "warning"


def _build_rule_note(duration_minutes: int, calculated_amount: Decimal, parking_rule: dict) -> str:
    """生成详情页可展示的收费说明。"""

    free_minutes = max(int(parking_rule.get("free_minutes", 0) or 0), 0)
    fee_per_hour = Decimal(str(parking_rule.get("fee_per_hour", "0") or "0")).quantize(Decimal("0.01"))
    daily_cap = Decimal(str(parking_rule.get("daily_cap", "0") or "0")).quantize(Decimal("0.01"))

    if duration_minutes <= free_minutes:
        return f"当前按免费时长 {free_minutes} 分钟计算，未产生停车费用。"

    note = f"当前按免费时长 {free_minutes} 分钟、每小时 {fee_per_hour:.2f} 元"
    if daily_cap > DECIMAL_ZERO:
        note += f"、单日封顶 {daily_cap:.2f} 元"
    return f"{note} 计算，当前费用为 {calculated_amount:.2f} 元。"


def _build_rule_summary(parking_rule: dict) -> str:
    """生成列表页和汇总区共用的收费规则摘要。"""

    free_minutes = max(int(parking_rule.get("free_minutes", 0) or 0), 0)
    fee_per_hour = Decimal(str(parking_rule.get("fee_per_hour", "0") or "0")).quantize(Decimal("0.01"))
    daily_cap = Decimal(str(parking_rule.get("daily_cap", "0") or "0")).quantize(Decimal("0.01"))
    overdue_hours = max(int(parking_rule.get("overdue_hours", 0) or 0), 0)

    summary = f"当前收费规则：免费 {free_minutes} 分钟，超出后按 {fee_per_hour:.2f} 元/小时向上计费"
    if daily_cap > DECIMAL_ZERO:
        summary += f"，单日封顶 {daily_cap:.2f} 元"
    if overdue_hours > 0:
        summary += f"，超过 {overdue_hours} 小时标记为超时在场"
    return summary + "。"


def _serialize_record(record: ParkingRecord, parking_rule: dict) -> dict:
    """将停车记录模型转换为列表页所需结构。"""

    duration_minutes, calculated_amount = _resolve_record_pricing(record, parking_rule)
    status_text, status_type = _resolve_display_status(record, duration_minutes, parking_rule)

    return {
        "id": record.id,
        "recordNo": record.record_no,
        "plate": record.plate_number,
        "enterAt": _format_datetime(record.entry_time),
        "leaveAt": _format_datetime(record.exit_time),
        "duration": _format_duration(duration_minutes, record.record_status == "在场"),
        "amount": f"{calculated_amount:.2f}",
        "payStatus": record.pay_status,
        "status": status_text,
        "type": status_type,
    }


def _serialize_record_detail(record: ParkingRecord, parking_rule: dict) -> dict:
    """将单条停车记录转换为详情页所需结构。"""

    duration_minutes, calculated_amount = _resolve_record_pricing(record, parking_rule)
    status_text, _ = _resolve_display_status(record, duration_minutes, parking_rule)
    rule_note = _build_rule_note(duration_minutes, calculated_amount, parking_rule)

    return {
        "id": record.id,
        "recordNo": record.record_no,
        "vehicleId": record.vehicle_id,
        "plate": record.plate_number,
        "entryGate": record.entry_gate or "--",
        "exitGate": record.exit_gate or "--",
        "enterAt": _format_datetime(record.entry_time),
        "leaveAt": _format_datetime(record.exit_time),
        "duration": _format_duration(duration_minutes, record.record_status == "在场"),
        "amount": f"{calculated_amount:.2f}",
        "payStatus": record.pay_status,
        "status": status_text,
        "pricingNote": rule_note,
        "remark": record.remark or "暂无备注",
        "entryImage": record.entry_image or "",
        "exitImage": record.exit_image or "",
    }


def _get_record_or_raise(pk: int) -> ParkingRecord:
    """按主键获取停车记录，不存在时抛出 404。"""

    record = ParkingRecord.objects.filter(pk=pk).first()
    if record is None:
        raise exceptions.NotFound("停车记录不存在。")
    return record


def _normalize_pay_status_queryset(queryset, pay_status: str):
    """按支付状态过滤记录列表。"""

    normalized_pay_status = pay_status.strip()
    if not normalized_pay_status:
        return queryset
    return queryset.filter(pay_status=normalized_pay_status)


def _normalize_date(value: str) -> date | None:
    """解析日期字符串，非法值返回空，避免前端误传时接口报错。"""

    normalized_value = value.strip()
    if not normalized_value:
        return None
    return parse_date(normalized_value)


def _build_record_queryset(keyword="", pay_status="", date_from="", date_to=""):
    """按列表页筛选条件构造统一查询集。"""

    queryset = ParkingRecord.objects.all().order_by("-entry_time")
    normalized_keyword = keyword.strip()

    if normalized_keyword:
        queryset = queryset.filter(
            Q(plate_number__icontains=normalized_keyword)
            | Q(record_status__icontains=normalized_keyword)
            | Q(record_no__icontains=normalized_keyword)
            | Q(pay_status__icontains=normalized_keyword)
        )

    queryset = _normalize_pay_status_queryset(queryset, pay_status)

    parsed_date_from = _normalize_date(date_from)
    parsed_date_to = _normalize_date(date_to)

    if parsed_date_from:
        queryset = queryset.filter(entry_time__date__gte=parsed_date_from)
    if parsed_date_to:
        queryset = queryset.filter(entry_time__date__lte=parsed_date_to)

    return queryset


def _filter_serialized_records(records: list[dict], status: str) -> list[dict]:
    """根据前端筛选值过滤已序列化后的展示状态。"""

    normalized_status = status.strip().lower()
    if not normalized_status:
        return records
    if normalized_status == "busy":
        return [record for record in records if record["type"] == "busy"]
    if normalized_status == "free":
        return [record for record in records if record["type"] == "free"]
    if normalized_status == "warning":
        return [record for record in records if record["type"] == "warning"]
    return []


def _get_serialized_records(keyword="", status="", pay_status="", date_from="", date_to="") -> list[dict]:
    """统一生成记录列表、汇总和导出共用的展示数据。"""

    parking_rule = get_runtime_config()["parking_rule"]
    queryset = _build_record_queryset(keyword, pay_status, date_from, date_to)
    records = [_serialize_record(record, parking_rule) for record in queryset]
    return _filter_serialized_records(records, status)


def list_records(keyword="", status="", pay_status="", date_from="", date_to=""):
    """按关键词、状态、支付状态和日期范围过滤停车记录。"""

    return _get_serialized_records(keyword, status, pay_status, date_from, date_to)


def get_record_summary(keyword="", status="", pay_status="", date_from="", date_to="") -> dict:
    """返回记录列表顶部统计卡片所需的汇总数据。"""

    records = _get_serialized_records(keyword, status, pay_status, date_from, date_to)
    parking_rule = get_runtime_config()["parking_rule"]
    total_amount = sum(Decimal(record["amount"]) for record in records if record["payStatus"] == "已支付")

    return {
        "totalCount": len(records),
        "inLotCount": sum(1 for record in records if record["status"] in {"在场", "超时在场"}),
        "departedCount": sum(1 for record in records if record["status"] == "已离场"),
        "unpaidCount": sum(1 for record in records if record["payStatus"] == "未支付"),
        "overdueCount": sum(1 for record in records if record["status"] == "超时在场"),
        "totalAmount": f"{total_amount:.2f}",
        "ruleSummary": _build_rule_summary(parking_rule),
    }


def export_records_csv(keyword="", status="", pay_status="", date_from="", date_to="") -> HttpResponse:
    """按当前筛选条件导出 CSV 文件。"""

    records = _get_serialized_records(keyword, status, pay_status, date_from, date_to)

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["记录编号", "车牌号", "入场时间", "离场时间", "停留时长", "停车费用", "支付状态", "记录状态"])

    for record in records:
        writer.writerow(
            [
                record["recordNo"],
                record["plate"],
                record["enterAt"],
                record["leaveAt"],
                record["duration"],
                record["amount"],
                record["payStatus"],
                record["status"],
            ]
        )

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response.write("\ufeff")
    response.write(buffer.getvalue())
    response["Content-Disposition"] = (
        f'attachment; filename="parking-records-{timezone.now().strftime("%Y%m%d-%H%M%S")}.csv"'
    )
    return response


def get_record_detail(pk: int) -> dict:
    """获取单条停车记录的详情数据。"""

    record = _get_record_or_raise(pk)
    parking_rule = get_runtime_config()["parking_rule"]
    return _serialize_record_detail(record, parking_rule)


def create_entry_record(validated_data: dict) -> dict:
    """模拟车辆入场，创建在场记录并同步占用车位。"""

    plate_number = validated_data["plate_number"].strip().upper()
    if _get_active_record_by_plate(plate_number) is not None:
        raise exceptions.ValidationError("该车辆已存在未完成的在场记录。")

    vehicle = _get_or_create_vehicle_by_plate(plate_number)
    space = _get_available_space(validated_data.get("space_id"))
    now = timezone.now()

    record = ParkingRecord.objects.create(
        record_no=_generate_record_no(),
        plate_number=plate_number,
        vehicle_id=vehicle.id,
        space_id=space.id,
        entry_gate=validated_data["entry_gate"].strip(),
        exit_gate=None,
        entry_time=now,
        exit_time=None,
        duration_minutes=0,
        amount=DECIMAL_ZERO,
        pay_status="未支付",
        record_status="在场",
        entry_image="",
        exit_image="",
        remark=validated_data.get("remark", "").strip() or "模拟入场创建",
        created_at=now,
        updated_at=now,
    )

    space.status = "占用"
    space.updated_at = now
    space.save(update_fields=["status", "updated_at"])

    parking_rule = get_runtime_config()["parking_rule"]
    return _serialize_record_detail(record, parking_rule)


def settle_exit_record(validated_data: dict) -> dict:
    """模拟车辆出场，结算费用并释放占用车位。"""

    plate_number = validated_data["plate_number"].strip().upper()
    record = _get_active_record_by_plate(plate_number)
    if record is None:
        raise exceptions.NotFound("未找到该车牌当前在场的停车记录。")

    now = timezone.now()
    parking_rule = get_runtime_config()["parking_rule"]

    # 先写入离场时间，再按最终时间点重新计算时长和费用。
    record.exit_time = now
    duration_minutes, calculated_amount = _resolve_record_pricing(record, parking_rule)

    record.exit_gate = validated_data["exit_gate"].strip()
    record.duration_minutes = duration_minutes
    record.amount = calculated_amount
    record.pay_status = "已支付"
    record.record_status = "已离场"
    record.remark = validated_data.get("remark", "").strip() or "模拟出场结算完成"
    record.updated_at = now
    record.save(
        update_fields=[
            "exit_gate",
            "exit_time",
            "duration_minutes",
            "amount",
            "pay_status",
            "record_status",
            "remark",
            "updated_at",
        ]
    )

    if record.space_id:
        ParkingSpace.objects.filter(pk=record.space_id).update(status="空闲", updated_at=now)

    return _serialize_record_detail(record, parking_rule)
