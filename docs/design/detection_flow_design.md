# ParkVision 识别接口数据流与时序设计

## 1. 文档目的

本文档用于说明 ParkVision 项目中“识别接口”从前端发起请求到后端返回结果的完整数据流与时序关系。

在前两份文档中，我们已经明确了：

- YOLO 在系统中的职责
- `ai/` 模块的内部文件分层

本文档进一步回答以下问题：

1. 用户上传图片后，系统内部按什么顺序处理。
2. 入口识别、出口识别、车位识别三种流程有什么区别。
3. Django 后端如何保存文件、调用 AI、整理结果并写入业务表。
4. 识别结果最终如何回到前端页面。

---

## 2. 当前系统中的识别入口

当前前端识别测试页通过后端接口访问识别能力：

```text
POST /api/detection/
```

后端对应模块为：

```text
backend/apps/detection/
```

现阶段接口已经具备演示骨架，后续只需要将其服务层替换为真实 AI 模块调用即可。

---

## 3. 识别接口的统一处理原则

无论是入口识别、出口识别还是停车区识别，都建议遵循同一套基础流程。

### 3.1 统一基础流程

1. 前端上传图片
2. Django 接收请求
3. 后端保存原始图片
4. 根据任务类型调用 AI 服务
5. 获得结构化识别结果
6. 根据业务场景决定是否更新数据库
7. 返回标准 JSON 给前端

### 3.2 统一设计目标

该设计应保证：

- 前端调用路径统一
- AI 模块只负责识别
- Django 负责业务判断
- 识别流程可复用、可扩展

---

## 4. 统一时序总览

从系统整体来看，建议识别链路按照以下时序执行：

```text
前端页面
   ↓ 上传图片
Django detection 接口
   ↓ 保存原图
AI service 层
   ↓ 调用 YOLO / OCR
返回结构化结果
   ↓
Django 业务层
   ↓ 写入记录 / 更新状态 / 组织响应
前端展示识别结果
```

这意味着：

- YOLO 不直接面对数据库
- 前端不直接依赖模型细节
- Django 起到“调度层”和“业务转换层”的作用

---

## 5. 入口识别流程设计

入口识别的核心目标是：

**识别进入小区的车辆及车牌，并生成一条新的入场停车记录。**

### 5.1 入口识别时序

推荐时序如下：

```text
1. 前端上传入口图片
2. detection 接口接收文件
3. Django 将图片保存到 media/raw/
4. Django 调用 ai.services.recognize_plate(image_path)
5. AI 返回车辆框、车牌框、OCR 结果
6. Django 判断车牌是否有效
7. Django 在 parking_records 中生成“在场”记录
8. Django 返回识别结果给前端
```

### 5.2 入口识别涉及的数据

输入：

- 原始图片
- 入口通道标识（可选）
- 任务类型：`entry`

AI 输出：

- 车辆框
- 车牌框
- 车牌号
- 识别置信度

业务输出：

- 新增一条停车记录
- 记录入场时间
- 记录入口名称
- 保存抓拍图路径

### 5.3 入口识别写库建议

可写入 `pv_parking_records` 表中的字段：

- `record_no`
- `plate_number`
- `entry_gate`
- `entry_time`
- `record_status = 在场`
- `entry_image`

如果能匹配到车辆主数据，还可以补：

- `vehicle_id`

---

## 6. 出口识别流程设计

出口识别的核心目标是：

**识别离场车辆，并将对应停车记录闭环。**

### 6.1 出口识别时序

推荐时序如下：

```text
1. 前端上传出口图片
2. detection 接口接收文件
3. Django 将图片保存到 media/raw/
4. Django 调用 ai.services.recognize_plate(image_path)
5. AI 返回车牌识别结果
6. Django 根据车牌匹配“当前在场记录”
7. Django 写入出场时间、停车时长、费用与支付状态
8. Django 返回识别结果与结算信息给前端
```

### 6.2 出口识别涉及的数据

输入：

- 原始图片
- 出口通道标识（可选）
- 任务类型：`exit`

AI 输出：

- 车辆框
- 车牌框
- 车牌号
- 识别置信度

业务输出：

- 更新原有停车记录
- 记录出场时间
- 计算停车时长
- 更新支付状态或费用展示

### 6.3 出口识别写库建议

更新 `pv_parking_records` 表中的字段：

- `exit_gate`
- `exit_time`
- `duration_minutes`
- `amount`
- `pay_status`
- `record_status = 已离场`
- `exit_image`

---

## 7. 停车区识别流程设计

停车区识别的核心目标是：

**识别停车区域中的车辆，并判断各车位是否空闲或占用。**

### 7.1 停车区识别时序

推荐时序如下：

```text
1. 前端上传停车区图片
2. detection 接口接收文件
3. Django 保存原始图片
4. Django 调用 ai.services.detect_space_status(image_path)
5. AI 先检测车辆，再结合车位区域判断状态
6. Django 根据结果更新 parking_spaces 状态
7. Django 返回车位状态结果给前端
```

### 7.2 停车区识别涉及的数据

输入：

- 停车区图像
- 任务类型：`parking`

AI 输出：

- 车辆框列表
- 每个车位的占用结果
- 结果图路径（可选）

业务输出：

- 更新 `pv_parking_spaces` 的状态字段
- 供首页和监控页读取最新占用率

### 7.3 车位状态写库建议

更新 `pv_parking_spaces` 表中的字段：

- `status`
- `updated_at`

如后续需要保留识别历史，可新增一张识别任务表单独记录。

---

## 8. detection 接口推荐参数设计

为了兼容三类识别任务，建议 `POST /api/detection/` 支持以下参数。

### 8.1 请求参数建议

表单字段：

- `file`：上传图片文件
- `task_type`：任务类型
- `location`：入口/出口/区域名称（可选）

### 8.2 task_type 建议枚举

- `entry`：入口识别
- `exit`：出口识别
- `parking`：停车区识别

### 8.3 请求示例

```text
POST /api/detection/
Content-Type: multipart/form-data

file=<image>
task_type=entry
location=东入口
```

---

## 9. detection 接口推荐响应格式

建议后端统一返回以下结构：

```json
{
  "task": "entry",
  "location": "东入口",
  "plate": "粤B·A2138",
  "confidence": "97.8%",
  "vehicle_type": "新能源轿车",
  "boxes": [
    {
      "label": "vehicle",
      "x1": 120,
      "y1": 88,
      "x2": 420,
      "y2": 310
    },
    {
      "label": "plate",
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
  "business": {
    "record_status": "在场",
    "record_no": "REC202603130001"
  },
  "result_image": "/media/results/entry_20260313_101523.jpg"
}
```

### 9.1 说明

- `task`：识别任务类型
- `boxes`：前端绘制检测框使用
- `steps`：前端流程步骤展示使用
- `business`：业务处理结果
- `result_image`：检测结果图路径

---

## 10. Django detection 服务层推荐改造方案

当前 `backend/apps/detection/services.py` 仍是演示数据逻辑，后续建议按以下方式改造。

### 10.1 当前阶段

当前服务层：

- 根据 preset 返回固定结果
- 用于前端展示与接口联调

### 10.2 后续真实改造目标

改造后应具备：

1. 接收 `task_type`
2. 根据任务类型调用不同 AI 服务
3. 组织统一返回结构
4. 必要时触发数据库写入

### 10.3 推荐伪代码

```python
def detect_image(image_path: str, task_type: str, location: str = "") -> dict:
    if task_type == "entry":
        result = recognize_plate(image_path)
        business = create_entry_record(result, location)
    elif task_type == "exit":
        result = recognize_plate(image_path)
        business = close_exit_record(result, location)
    elif task_type == "parking":
        result = detect_space_status(image_path)
        business = update_space_status(result)
    else:
        raise ValueError("不支持的任务类型")

    return build_detection_response(result, business)
```

---

## 11. 与数据库表的关联关系

识别结果与现有数据库表的关系建议如下。

### 11.1 与 `pv_parking_records` 的关系

入口识别与出口识别都应关联该表：

- 入口：新增记录
- 出口：更新记录

### 11.2 与 `pv_parking_spaces` 的关系

停车区识别应关联该表：

- 更新车位状态

### 11.3 与 `pv_vehicles` 的关系

入口/出口识别时可根据车牌号匹配车辆主数据：

- 若匹配成功，关联 `vehicle_id`
- 若匹配失败，仍允许以临时车辆方式记录

---

## 12. 识别结果图与业务图的保存策略

建议把识别过程中的图像结果分为三类保存。

### 12.1 原始图片

目录：

```text
backend/media/raw/
```

### 12.2 检测结果图

目录：

```text
backend/media/results/
```

### 12.3 停车记录抓拍图

目录：

```text
backend/media/records/
```

### 12.4 推荐保存逻辑

- 原图始终保存
- 结果图按需保存
- 与业务记录相关的入口/出口图同时保存到记录目录

---

## 13. 三类识别流程的差异总结

| 流程类型 | AI 核心能力 | 业务处理重点 | 数据库影响 |
|---|---|---|---|
| 入口识别 | 车辆检测 + 车牌检测 + OCR | 创建入场记录 | 新增 `parking_records` |
| 出口识别 | 车辆检测 + 车牌检测 + OCR | 闭合停车记录 | 更新 `parking_records` |
| 停车区识别 | 车辆检测 + 车位区域判断 | 更新车位状态 | 更新 `parking_spaces` |

---

## 14. 推荐的实现顺序

为了减少接入难度，建议按以下顺序实现。

### 第一步：完成 detection 接口参数规范

目标：

- 明确 `task_type`
- 明确统一返回字段

### 第二步：先接入口识别

原因：

- 入口识别最容易形成完整演示链路
- 车牌识别是整个系统最核心的展示点

### 第三步：接出口识别

原因：

- 可以闭合停车记录
- 与停车业务关系最紧密

### 第四步：接停车区识别

原因：

- 该部分更偏监控统计
- 可以在前两者稳定后再补

---

## 15. 当前阶段结论

本文档完成后，ParkVision 的识别链路已经形成三层连续设计：

1. 《YOLO 模型对接方案》：明确 YOLO 的系统职责
2. 《AI 模块内部设计与接口约定》：明确 `ai/` 模块分层
3. 《识别接口数据流与时序设计》：明确前后端与数据库的完整流转

这意味着后续已经可以正式开始：

- 设计 detection 接口真实参数
- 编写 `ai/services/` 的真实函数骨架
- 将 detection 演示服务替换为真实 AI 调用链路

---

## 16. 下一步建议

接下来建议继续补一份更贴近代码实现的文档：

**《AI 服务函数签名与返回字段规范》**

建议内容包括：

1. `detect_vehicle()` 的输入输出定义
2. `recognize_plate()` 的输入输出定义
3. `detect_space_status()` 的输入输出定义
4. 检测框、车牌、步骤、业务结果的标准字段说明

完成后，就可以开始真正写 `ai/models/` 与 `ai/services/` 的 Python 文件骨架。
