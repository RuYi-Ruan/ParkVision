# ParkVision AI 模块内部设计与接口约定

## 1. 文档目的

本文档用于进一步细化 ParkVision 项目中 `ai/` 模块的内部职责、文件划分、输入输出格式以及与 Django 后端的调用关系。

在上一篇《YOLO 模型对接方案》的基础上，本文档更关注“如何落地实现”，目标是为后续真实接入 YOLO、OCR 与车位状态判断提供一份统一的开发规范。

本文档重点解决以下问题：

1. `ai/` 目录下各层文件分别负责什么。
2. 模型层、服务层、工具层如何协作。
3. Django 后端调用 AI 模块时应该传什么、拿什么。
4. 前端识别页展示所需的数据结构如何统一。

---

## 2. AI 模块在系统中的定位

在 ParkVision 中，`ai/` 模块属于系统的“感知层”，主要负责：

- 从图像中检测车辆
- 从图像中检测车牌
- 对车牌图像执行 OCR 识别
- 基于车辆检测结果判断车位占用状态

`ai/` 模块不负责：

- 业务表写入数据库
- 用户、车辆、车位管理逻辑
- 接口权限校验
- 前端页面展示

这些内容仍由 Django 后端负责。

因此，AI 模块的边界应该保持为：

**输入一张图片或图片路径，输出结构化识别结果。**

---

## 3. 当前目录与推荐职责划分

当前 `ai/` 目录如下：

```text
ai/
├─ weights/
├─ configs/
├─ datasets/
├─ models/
├─ services/
├─ utils/
├─ outputs/
├─ train/
└─ notebooks/
```

推荐职责如下。

### 3.1 weights/

作用：

- 存放训练好的模型权重文件

推荐内容：

- `vehicle_yolo.pt`：车辆检测模型权重
- `plate_yolo.pt`：车牌检测模型权重
- `best.pt`：如后续合并训练，可存放统一最佳权重

说明：

- Django 不应直接读取该目录
- 权重文件应由 `models/` 统一加载

### 3.2 configs/

作用：

- 存放模型配置文件与数据集配置文件

推荐内容：

- `vehicle.yaml`
- `plate.yaml`
- `parking_space.yaml`

说明：

- 训练阶段与推理阶段共用配置来源
- 便于后期更换模型参数时统一维护

### 3.3 datasets/

作用：

- 存放训练与测试数据集

推荐内容：

- `vehicle/`：车辆检测数据集
- `plate/`：车牌检测数据集
- `sample/`：前端演示和模型调试用的样例图片

说明：

- 毕业设计展示时，`sample/` 可以作为固定演示素材
- 实际运行时，前端上传图片不会直接写进此目录

### 3.4 models/

作用：

- 封装模型加载与单模型推理能力

推荐文件及职责：

#### `vehicle_detector.py`

负责：

- 加载车辆检测模型
- 接收图片路径或图像对象
- 返回车辆检测框列表

#### `plate_detector.py`

负责：

- 加载车牌检测模型
- 返回车牌检测框列表

#### `ocr_recognizer.py`

负责：

- 对车牌裁剪图执行 OCR
- 返回识别出的车牌字符串及置信度

#### `parking_status.py`

负责：

- 读取预定义车位区域
- 基于车辆框判断车位占用状态

说明：

- `models/` 只做“模型能力”
- 不应在这里直接写业务逻辑

### 3.5 services/

作用：

- 对外提供组合后的感知服务

推荐文件及职责：

#### `detect_vehicle.py`

负责：

- 调用 `vehicle_detector.py`
- 返回整理后的车辆检测结果

#### `detect_plate.py`

负责：

- 调用 `plate_detector.py`
- 返回整理后的车牌检测结果

#### `recognize_plate.py`

负责：

- 调用车牌检测
- 裁剪车牌图像
- 调用 OCR 识别
- 返回完整车牌识别结果

#### `detect_space_status.py`

负责：

- 调用车辆检测
- 结合车位坐标区域
- 输出每个车位的状态结果

说明：

- Django 后端应优先调用 `services/`
- `services/` 才是 AI 模块真正对外暴露的能力入口

### 3.6 utils/

作用：

- 存放图像、文件、绘图、几何计算等辅助函数

推荐文件及职责：

#### `image_utils.py`

负责：

- 图片加载
- 图片保存
- 裁剪区域
- 尺寸转换

#### `draw_utils.py`

负责：

- 在图像上绘制检测框
- 绘制标签
- 保存结果图

#### `file_utils.py`

负责：

- 路径生成
- 文件名规范化
- 输出目录创建

#### `geometry_utils.py`

负责：

- 计算 IOU
- 判断框与车位区域是否重叠
- 计算中心点归属

---

## 4. 推荐的分层调用原则

为了保证代码结构清晰，建议严格遵守以下调用方向：

```text
Django backend
   ↓
ai/services/
   ↓
ai/models/
   ↓
ai/utils/
```

### 4.1 不推荐的调用方式

不建议 Django 直接调用：

- `ai/models/vehicle_detector.py`
- `ai/models/plate_detector.py`

原因：

- Django 会知道太多模型细节
- 后期改模型会影响后端接口层
- 不利于维护和论文表达

### 4.2 推荐的调用方式

推荐由 Django 调用：

```python
from ai.services.recognize_plate import recognize_plate
from ai.services.detect_space_status import detect_space_status
```

这样可以保持：

- 感知层独立
- 业务层清晰
- 接口返回统一

---

## 5. 推荐的统一输入形式

AI 模块对外应尽量统一输入参数，避免每个函数风格不一致。

### 5.1 推荐输入方式

优先推荐：

```python
image_path: str
```

原因：

- Django 接收上传图片后，本来就会先保存文件
- 图片路径最容易在模块之间传递
- 日志与结果图保存更方便

### 5.2 可选输入方式

后续如有需要，也可以扩展：

```python
image_array: numpy.ndarray
```

但当前毕业设计阶段，不建议一开始就增加过多输入形式。

### 5.3 推荐统一函数签名

例如：

```python
def detect_vehicle(image_path: str) -> dict:
    ...
```

```python
def recognize_plate(image_path: str) -> dict:
    ...
```

```python
def detect_space_status(image_path: str) -> dict:
    ...
```

---

## 6. 推荐的统一输出格式

为了便于前端展示和 Django 接口返回，建议 AI 服务统一返回字典结构，而不是直接返回 YOLO 原始对象。

### 6.1 车辆检测输出

推荐格式：

```python
{
    "task": "vehicle_detection",
    "image_path": "backend/media/raw/test.jpg",
    "boxes": [
        {
            "label": "vehicle",
            "confidence": 0.96,
            "x1": 120,
            "y1": 88,
            "x2": 420,
            "y2": 310
        }
    ]
}
```

### 6.2 车牌识别输出

推荐格式：

```python
{
    "task": "plate_recognition",
    "plate": "粤B·A2138",
    "confidence": 0.94,
    "vehicle_type": "car",
    "location": "东入口",
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
        {"label": "车辆检测", "value": "1 个目标"},
        {"label": "车牌定位", "value": "1 个车牌框"},
        {"label": "OCR 识别", "value": "粤B·A2138"}
    ]
}
```

### 6.3 车位状态输出

推荐格式：

```python
{
    "task": "space_status_detection",
    "spaces": [
        {"space_code": "A-01", "status": "空闲"},
        {"space_code": "A-02", "status": "占用"},
        {"space_code": "A-03", "status": "空闲"}
    ],
    "vehicles": [
        {
            "label": "vehicle",
            "confidence": 0.95,
            "x1": 66,
            "y1": 144,
            "x2": 224,
            "y2": 310
        }
    ]
}
```

---

## 7. Django detection 模块与 AI 模块的关系

### 7.1 当前 detection 模块职责

`backend/apps/detection/` 负责：

- 接收前端上传图片
- 调用 AI 服务
- 整理接口返回结果
- 必要时落库或保存图片

### 7.2 推荐调用关系

#### 场景一：入口/出口识别

```python
result = recognize_plate(image_path)
```

#### 场景二：停车区状态识别

```python
result = detect_space_status(image_path)
```

### 7.3 推荐 detection 服务层流程

后端识别服务的推荐流程如下：

1. 接收上传图片
2. 保存到 `backend/media/raw/`
3. 根据任务类型调用不同 AI 服务
4. 获得结构化识别结果
5. 写入 `media/results/` 或 `media/records/`
6. 返回统一接口结果给前端

---

## 8. 前后端接口字段统一建议

为了让前端识别页保持稳定，建议 `backend/apps/detection/` 输出字段尽量固定。

### 8.1 建议保留的核心字段

- `task`
- `plate`
- `confidence`
- `vehicle_type`
- `location`
- `boxes`
- `steps`
- `result_image`

### 8.2 前端页面依赖说明

前端识别测试页已经有以下展示需求：

- 检测类型
- 车牌号
- 置信度
- 检测框
- 处理流程步骤
- 结果图或原图预览

因此后端真实接 YOLO 时，最好不要频繁变动字段名称。

---

## 9. 推荐的结果图保存策略

为了便于演示与调试，建议每次识别后都生成一张带检测框的结果图。

### 9.1 原始图保存目录

建议保存到：

```text
backend/media/raw/
```

### 9.2 结果图保存目录

建议保存到：

```text
backend/media/results/
```

### 9.3 停车记录抓拍图保存目录

如识别结果与停车记录相关，建议保存到：

```text
backend/media/records/
```

### 9.4 推荐命名方式

例如：

```text
entry_20260313_101523.jpg
exit_20260313_102402.jpg
space_20260313_103114.jpg
```

说明：

- 带有时间戳的命名更便于追踪
- 后续写论文截图时也容易找到对应图片

---

## 10. 推荐的车位状态判断逻辑

`parking_status.py` 建议采用以下规则：

### 10.1 输入

- 停车区图像路径
- 车辆检测框列表
- 车位区域配置

### 10.2 输出

- 每个车位的状态结果

### 10.3 判断规则

可选规则如下：

#### 规则一：中心点落入法

如果车辆框中心点落入某车位区域，则认定该车位被占用。

优点：

- 简单
- 易实现

#### 规则二：重叠面积法

如果车辆框与车位区域的重叠比例超过阈值，则认定该车位被占用。

优点：

- 更稳
- 更适合复杂场景

### 推荐结论

建议优先采用：

**重叠面积法 + 阈值判断**

例如：

- IOU 或覆盖率大于 `0.2 ~ 0.3` 视为占用

---

## 11. 推荐的模型初始化方式

为了避免每次请求都重复加载模型，建议模型对象在模块级别初始化。

### 示例思路

```python
class VehicleDetector:
    def __init__(self, weight_path: str):
        self.model = ...

    def predict(self, image_path: str):
        ...


vehicle_detector = VehicleDetector("ai/weights/vehicle_yolo.pt")
```

说明：

- 首次加载略慢，但后续请求速度更稳定
- 更适合 Django 常驻进程

---

## 12. 推荐的日志与异常处理方式

AI 模块在接入时，建议考虑以下异常场景：

- 权重文件不存在
- 图片读取失败
- 检测结果为空
- OCR 未识别出有效车牌
- 车位配置文件缺失

### 推荐原则

1. `models/` 层抛出明确异常
2. `services/` 层统一整理异常信息
3. Django 层转为标准 API 返回

### 推荐示例

```python
{
    "task": "plate_recognition",
    "plate": "",
    "confidence": 0,
    "message": "未识别到有效车牌"
}
```

---

## 13. 推荐的第一阶段真实接入顺序

为了降低接入难度，建议按以下顺序实现：

### 第一阶段：车辆检测模型接入

目标：

- 完成车辆检测
- 可以返回检测框

### 第二阶段：车牌检测与 OCR 接入

目标：

- 跑通车牌识别闭环
- 支持前端识别测试页展示

### 第三阶段：停车区车位状态判断

目标：

- 完成车位占用分析
- 支持监控页真实数据化

### 第四阶段：与停车记录联动

目标：

- 入口识别自动生成停车记录
- 出口识别自动闭合停车记录

---

## 14. 与论文撰写的对应建议

在毕业设计论文中，可以将本模块描述为：

### 14.1 模型层

负责深度学习模型加载与目标检测推理。

### 14.2 服务层

负责将检测、定位、OCR 与车位状态判断等能力封装为可被后端业务系统调用的接口。

### 14.3 业务调用层

由 Django 后端调用 AI 服务，将视觉识别结果转化为停车记录、车位状态和管理页面展示数据。

这种描述方式与工程实现一致，便于答辩时说明系统结构。

---

## 15. 当前阶段结论

在完成本文档后，ParkVision 的 AI 模块对接已经具备以下条件：

- 感知层职责清晰
- 文件分层明确
- 输入输出格式初步统一
- Django 与 AI 的调用边界清晰
- 前端识别页的数据结构有了稳定依据

下一步即可继续补一份更贴近实现的文档：

**《识别接口数据流与时序设计》**

该文档建议进一步说明：

1. 前端上传图片后的完整处理顺序
2. Django 保存文件、调用 AI、返回结果的时序
3. 入场识别、出场识别、车位识别三种流程的差异
4. 数据库表如何与识别结果关联
