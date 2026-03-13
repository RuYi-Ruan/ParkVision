# ParkVision AI 服务函数签名与返回字段规范

## 1. 文档目的

本文档用于统一 ParkVision 项目中 AI 服务层的函数签名、输入参数、返回结构和字段命名规范。

前面的三份文档已经分别解决了：

1. YOLO 在系统中的职责
2. `ai/` 模块的内部设计
3. 识别接口的数据流与时序

本文档进一步回答：

1. `ai/services/` 中的函数具体该怎么定义。
2. 每个函数输入什么、输出什么。
3. 返回字段如何保持前后端统一。
4. 后续真实接入模型时，哪些字段必须稳定。

---

## 2. 设计原则

AI 服务层的设计建议遵循以下原则：

### 2.1 函数签名统一

优先采用统一的输入风格，例如：

```python
def recognize_plate(image_path: str, location: str = "") -> dict:
    ...
```

这样有利于：

- Django 后端统一调用
- 记录日志
- 后续切换本地图片或样例图片调试

### 2.2 返回结构统一

AI 服务层不应直接返回 YOLO 原始对象，而应返回已经整理好的字典结构。

### 2.3 命名风格统一

建议：

- Python 内部变量使用蛇形命名
- 返回给 Django/前端的字段名使用前端已经在用的驼峰风格或文档约定字段

### 2.4 错误信息可读

即使识别失败，也应返回结构化结果，而不是仅抛异常。

---

## 3. 推荐的基础数据结构

为了便于复用，建议 AI 服务层输出以下几类标准结构。

### 3.1 检测框结构

```python
{
    "label": "vehicle",
    "confidence": 0.96,
    "x1": 120,
    "y1": 88,
    "x2": 420,
    "y2": 310
}
```

字段说明：

- `label`：目标类别，例如 `vehicle`、`plate`
- `confidence`：检测置信度
- `x1/y1/x2/y2`：矩形框坐标

### 3.2 步骤结构

```python
{
    "label": "OCR 识别",
    "value": "粤B·A2138"
}
```

字段说明：

- `label`：步骤名称
- `value`：该步骤的处理结果

### 3.3 业务结果结构

```python
{
    "recordStatus": "在场",
    "recordNo": "REC202603130001"
}
```

字段说明：

- `recordStatus`：业务状态
- `recordNo`：停车记录编号

---

## 4. detect_vehicle() 规范

### 4.1 函数职责

负责对输入图像执行车辆检测，并返回车辆框列表。

### 4.2 推荐函数签名

```python
def detect_vehicle(image_path: str, location: str = "") -> dict:
    ...
```

### 4.3 输入参数

- `image_path`：待识别图片路径
- `location`：场景位置，可选，例如 `东入口`、`地下 C 区`

### 4.4 推荐返回结构

```python
{
    "task": "vehicle_detection",
    "location": "地下 C 区",
    "plate": "",
    "confidence": "96.2%",
    "vehicleType": "car",
    "boxes": [
        {
            "label": "vehicle",
            "confidence": 0.962,
            "x1": 120,
            "y1": 88,
            "x2": 420,
            "y2": 310
        }
    ],
    "steps": [
        {"label": "图像加载", "value": "成功"},
        {"label": "车辆检测", "value": "检测到 1 个车辆目标"}
    ],
    "resultImage": "/media/results/vehicle_xxx.jpg"
}
```

### 4.5 说明

- 车辆检测本身不一定返回车牌号
- `plate` 可以为空字符串
- `vehicleType` 可先返回通用值 `car`

---

## 5. detect_plate() 规范

### 5.1 函数职责

负责检测图像中的车牌区域。

### 5.2 推荐函数签名

```python
def detect_plate(image_path: str, location: str = "") -> dict:
    ...
```

### 5.3 推荐返回结构

```python
{
    "task": "plate_detection",
    "location": "东入口",
    "plate": "",
    "confidence": "94.7%",
    "vehicleType": "car",
    "boxes": [
        {
            "label": "plate",
            "confidence": 0.947,
            "x1": 198,
            "y1": 244,
            "x2": 286,
            "y2": 279
        }
    ],
    "steps": [
        {"label": "图像加载", "value": "成功"},
        {"label": "车牌定位", "value": "检测到 1 个车牌框"}
    ],
    "resultImage": "/media/results/plate_xxx.jpg"
}
```

---

## 6. recognize_plate() 规范

### 6.1 函数职责

负责完成“车牌检测 + 车牌裁剪 + OCR 识别”的完整流程，是入口识别与出口识别最核心的服务函数。

### 6.2 推荐函数签名

```python
def recognize_plate(image_path: str, location: str = "", task_type: str = "entry") -> dict:
    ...
```

### 6.3 输入参数

- `image_path`：待识别图片路径
- `location`：位置名称，例如 `东入口`
- `task_type`：任务类型，常见值为 `entry` 或 `exit`

### 6.4 推荐返回结构

```python
{
    "task": "entry",
    "location": "东入口",
    "plate": "粤B·A2138",
    "confidence": "97.8%",
    "vehicleType": "新能源轿车",
    "boxes": [
        {
            "label": "vehicle",
            "confidence": 0.96,
            "x1": 120,
            "y1": 88,
            "x2": 420,
            "y2": 310
        },
        {
            "label": "plate",
            "confidence": 0.93,
            "x1": 198,
            "y1": 244,
            "x2": 286,
            "y2": 279
        }
    ],
    "steps": [
        {"label": "车辆检测", "value": "已完成"},
        {"label": "车牌定位", "value": "已完成"},
        {"label": "OCR 识别", "value": "粤B·A2138"}
    ],
    "resultImage": "/media/results/entry_xxx.jpg"
}
```

### 6.5 说明

- 这个函数应优先作为 Django detection 模块的入口能力
- 如果 OCR 未识别成功，`plate` 应返回空字符串，但结构仍需完整

---

## 7. detect_space_status() 规范

### 7.1 函数职责

负责在停车区图像中检测车辆，并结合车位区域配置判断车位占用状态。

### 7.2 推荐函数签名

```python
def detect_space_status(image_path: str, location: str = "") -> dict:
    ...
```

### 7.3 推荐返回结构

```python
{
    "task": "parking",
    "location": "地下 C 区",
    "plate": "",
    "confidence": "95.4%",
    "vehicleType": "car",
    "boxes": [
        {
            "label": "vehicle",
            "confidence": 0.954,
            "x1": 66,
            "y1": 144,
            "x2": 224,
            "y2": 310
        }
    ],
    "steps": [
        {"label": "车辆检测", "value": "检测到 3 个车辆目标"},
        {"label": "区域映射", "value": "完成车位区域重叠判断"},
        {"label": "状态生成", "value": "输出 12 个车位状态"}
    ],
    "spaces": [
        {"spaceCode": "C-01", "status": "空闲"},
        {"spaceCode": "C-02", "status": "占用"},
        {"spaceCode": "C-03", "status": "空闲"}
    ],
    "resultImage": "/media/results/parking_xxx.jpg"
}
```

### 7.4 说明

- `spaces` 是该函数的关键输出
- 停车区识别不一定有车牌结果，因此 `plate` 可以为空

---

## 8. 推荐的统一失败返回

当 AI 服务识别失败时，建议不要直接中断为不可读异常，而是返回统一结构。

### 8.1 推荐失败结果

```python
{
    "task": "entry",
    "location": "东入口",
    "plate": "",
    "confidence": "0%",
    "vehicleType": "",
    "boxes": [],
    "steps": [
        {"label": "图像加载", "value": "成功"},
        {"label": "识别结果", "value": "未检测到有效目标"}
    ],
    "message": "未检测到有效车辆或车牌",
    "resultImage": ""
}
```

### 8.2 说明

- 前端依然可以展示“识别失败”状态
- Django 后端也更容易继续走统一响应逻辑

---

## 9. Django detection 服务层推荐对接方式

`backend/apps/detection/services.py` 后续可按以下规则对接。

### 9.1 场景映射建议

- `task_type=entry` -> `recognize_plate(..., task_type="entry")`
- `task_type=exit` -> `recognize_plate(..., task_type="exit")`
- `task_type=parking` -> `detect_space_status(...)`

### 9.2 Django 追加的业务字段

AI 服务返回基础识别结果后，Django 可以追加：

```python
{
    "business": {
        "recordStatus": "在场",
        "recordNo": "REC202603130001"
    }
}
```

或：

```python
{
    "business": {
        "updatedSpaces": 12,
        "occupiedCount": 8
    }
}
```

### 9.3 推荐职责划分

- AI 服务：负责“识别结果”
- Django 服务：负责“业务结果”

---

## 10. 与前端字段的对应建议

为了让前端识别页保持稳定，建议以下字段尽量固定：

- `task`
- `location`
- `plate`
- `confidence`
- `vehicleType`
- `boxes`
- `steps`
- `resultImage`
- `business`

当前前端识别页已经围绕这些字段设计，因此后续真实接入模型时应尽量保持兼容。

---

## 11. 推荐的最小实现顺序

在真正开始写 AI 代码时，建议最小实现顺序如下：

1. 先写 `detect_vehicle()` 的函数骨架
2. 再写 `detect_plate()` 的函数骨架
3. 再写 `recognize_plate()` 的组合逻辑
4. 最后写 `detect_space_status()`

原因：

- 车辆检测和车牌检测是基础能力
- 车牌识别依赖二者组合
- 车位状态判断依赖车辆检测与几何逻辑

---

## 12. 当前阶段结论

完成本文档后，ParkVision 的 AI 对接文档链路已经完整：

1. `yolo_integration.md`
2. `ai_module_design.md`
3. `detection_flow_design.md`
4. `ai_service_contract.md`

这四份文档已经足够支撑后续：

- 论文撰写
- 系统设计说明
- 真实 AI 服务骨架实现
- detection 接口重构

在不启动模型训练的前提下，当前思路整理工作已经基本完成。
