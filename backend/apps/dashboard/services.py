"""dashboard 模块的服务层。

首页统计优先从数据库读取，只有文案本身保持为固定配置。
"""

from decimal import Decimal

from django.db.models import Avg
from django.utils import timezone

from apps.parking.models import ParkingSpace
from apps.records.models import ParkingRecord


def get_dashboard_module_info():
    """返回 dashboard 模块说明，便于接口联调时排查挂载状态。"""
    return {
        "module": "dashboard",
        "description": "Dashboard statistics module.",
    }


def _safe_percentage(numerator: int, denominator: int) -> str:
    """将占比转换为带百分号的字符串，避免出现除零错误。"""
    if denominator <= 0:
        return "0%"
    return f"{round((numerator / denominator) * 100, 1)}%"


def _format_avg_duration(avg_minutes: Decimal | float | int | None) -> str:
    """把平均停车分钟数格式化为更直观的小时文本。"""
    if not avg_minutes:
        return "0h"
    return f"{round(float(avg_minutes) / 60, 1)}h"


def get_dashboard_overview():
    """从数据库汇总首页概览、统计卡片和最近入场记录。"""
    today = timezone.localdate()
    total_spaces = ParkingSpace.objects.count()
    free_spaces = ParkingSpace.objects.filter(status="空闲").count()
    busy_spaces = ParkingSpace.objects.filter(status="占用").count()
    active_records = ParkingRecord.objects.filter(record_status="在场").count()
    today_entries = ParkingRecord.objects.filter(entry_time__date=today).count()
    average_duration = (
        ParkingRecord.objects.filter(exit_time__isnull=False, duration_minutes__gt=0).aggregate(avg=Avg("duration_minutes"))[
            "avg"
        ]
    )

    recent_records = [
        {
            "plate": record.plate_number,
            "time": timezone.localtime(record.entry_time).strftime("%H:%M"),
            "gate": record.entry_gate or "未知入口",
        }
        for record in ParkingRecord.objects.order_by("-entry_time")[:4]
    ]

    return {
        "overview": {
            "eyebrow": "今日运营概览",
            "title": "停车场状态稳定，识别链路在线。",
            "description": "首页数据已经切换为数据库统计结果，可继续作为后续联调的基础面板。",
            "metrics": [
                {"label": "当前占用率", "value": _safe_percentage(busy_spaces, total_spaces)},
                {"label": "平均停留时长", "value": _format_avg_duration(average_duration)},
            ],
        },
        "stats": [
            {
                "label": "总车位",
                "value": str(total_spaces),
                "trend": "实时",
                "footnote": "数据库中的全部车位总数",
                "type": "positive",
            },
            {
                "label": "空闲车位",
                "value": str(free_spaces),
                "trend": "实时",
                "footnote": "当前状态为空闲的车位数量",
                "type": "neutral",
            },
            {
                "label": "在场车辆",
                "value": str(active_records),
                "trend": "实时",
                "footnote": "停车记录状态为在场的车辆数量",
                "type": "warning",
            },
            {
                "label": "今日进场",
                "value": str(today_entries),
                "trend": today.strftime("%m-%d"),
                "footnote": "按入场时间统计的当日记录数",
                "type": "positive",
            },
        ],
        "recent_records": recent_records,
    }
