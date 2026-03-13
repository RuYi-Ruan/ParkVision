"""系统设置模块的服务层。

当前阶段配置项使用 JSON 文件持久化，优点是：
1. 不依赖新增数据库表；
2. 前后端可以先把配置读写流程跑通；
3. 后续若切换为数据库存储，接口结构可以保持不变。
"""

from __future__ import annotations

import json
from copy import deepcopy

from django.conf import settings
from django.utils import timezone

# 配置文件放在项目数据目录中，方便后续作为初始化材料统一管理。
CONFIG_PATH = settings.BASE_DIR.parent / "data" / "runtime" / "system_settings.json"

DEFAULT_CONFIG = {
    "parking_rule": {
        "free_minutes": 15,
        "fee_per_hour": "6.00",
        "daily_cap": "48.00",
        "overdue_hours": 24,
    },
    "recognition": {
        "detect_confidence": "0.45",
        "ocr_confidence": "0.60",
        "yolo_model_path": "ai/weights/vehicle_yolo.pt",
        "plate_model_path": "ai/weights/plate_yolo.pt",
    },
    "runtime": {
        "default_zone": "主停车区 A 区",
        "monitor_refresh_seconds": 30,
        "auto_export_days": 30,
        "retain_days": 365,
    },
}


def _ensure_config_file():
    """确保配置文件目录和默认配置文件存在。"""

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_raw_config() -> dict:
    """读取原始配置内容，供业务层复用。"""

    _ensure_config_file()
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def get_runtime_config() -> dict:
    """返回不带展示字段的原始系统配置。"""

    return _load_raw_config()


def load_system_config() -> dict:
    """读取系统设置并补充更新时间。"""

    config_data = _load_raw_config()
    return {
        **config_data,
        "updated_at": timezone.localtime().strftime("%Y-%m-%d %H:%M"),
    }


def save_system_config(validated_data: dict) -> dict:
    """保存系统设置，并返回带更新时间的最新配置。"""

    _ensure_config_file()
    next_config = deepcopy(validated_data)
    CONFIG_PATH.write_text(json.dumps(next_config, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        **next_config,
        "updated_at": timezone.localtime().strftime("%Y-%m-%d %H:%M"),
    }
