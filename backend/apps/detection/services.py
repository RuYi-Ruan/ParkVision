"""detection 模块的服务层。

当前阶段先提供一个可真实调用的识别接口骨架，返回结构与后续 AI
推理结果保持一致。等 ai/ 模块准备好之后，可以在这里无缝替换为
真正的模型调用逻辑。
"""

from pathlib import Path


DETECT_PRESETS = [
    {
        "id": "entry",
        "label": "入口识别",
        "plate": "粤B·A2138",
        "task": "入口车牌检测",
        "confidence": "98.1%",
        "vehicleType": "新能源轿车",
        "location": "东入口 2 号道",
        "boxStyle": {"left": "18%", "top": "56%", "width": "30%", "height": "14%"},
        "steps": [
            {"label": "车辆检测", "value": "已锁定目标车辆"},
            {"label": "车牌定位", "value": "检测框已生成"},
            {"label": "OCR 识别", "value": "输出有效车牌号"},
        ],
    },
    {
        "id": "parking",
        "label": "车位占用",
        "plate": "粤B·7P221",
        "task": "车位区域识别",
        "confidence": "96.4%",
        "vehicleType": "商务车",
        "location": "地下 C 区 08 车位",
        "boxStyle": {"left": "44%", "top": "38%", "width": "34%", "height": "24%"},
        "steps": [
            {"label": "区域映射", "value": "车位轮廓已匹配"},
            {"label": "占用判断", "value": "当前状态为占用"},
            {"label": "结果同步", "value": "待写入停车记录"},
        ],
    },
    {
        "id": "exit",
        "label": "出口识别",
        "plate": "粤B·Q8M61",
        "task": "出口结算识别",
        "confidence": "97.3%",
        "vehicleType": "SUV",
        "location": "南出口 1 号道",
        "boxStyle": {"left": "22%", "top": "50%", "width": "28%", "height": "13%"},
        "steps": [
            {"label": "目标追踪", "value": "出口车辆已锁定"},
            {"label": "车牌识别", "value": "结果稳定输出"},
            {"label": "离场结算", "value": "待联动计费模块"},
        ],
    },
]


def get_detection_module_info():
    """返回 detection 模块说明信息。"""
    return {
        "module": "detection",
        "description": "AI detection API integration module.",
    }


def list_detection_presets():
    """返回识别测试页使用的预设结果列表。"""
    return DETECT_PRESETS


def _guess_preset_id(filename: str) -> str:
    """根据文件名做一个轻量推断，便于演示时更贴近“真实识别”。"""
    lower_name = filename.lower()
    if "exit" in lower_name or "out" in lower_name:
        return "exit"
    if "park" in lower_name or "space" in lower_name:
        return "parking"
    return "entry"


def detect_image(file_name: str = "", preset_id: str = ""):
    """返回一条与真实推理接口兼容的识别结果。

    参数优先级：
    1. 前端显式传入的 preset_id
    2. 根据上传文件名自动推断
    3. 默认回退到入口识别
    """
    resolved_id = preset_id or _guess_preset_id(Path(file_name).name)
    return next((item for item in DETECT_PRESETS if item["id"] == resolved_id), DETECT_PRESETS[0])
