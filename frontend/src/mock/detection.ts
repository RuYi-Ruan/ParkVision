import type { DetectPreset } from "./types";

// 识别测试页通过预设数据模拟不同场景，便于在后端未接入前完成交互设计。
export const detectPresets: DetectPreset[] = [
  {
    id: "entry",
    label: "入口识别",
    plate: "粤B·A2138",
    task: "入口车牌检测",
    confidence: "98.1%",
    vehicleType: "新能源轿车",
    location: "东入口 2 号道",
    boxStyle: { left: "18%", top: "56%", width: "30%", height: "14%" },
    steps: [
      { label: "车辆检测", value: "已锁定目标车辆" },
      { label: "车牌定位", value: "检测框已生成" },
      { label: "OCR 识别", value: "输出有效车牌号" },
    ],
  },
  {
    id: "parking",
    label: "车位占用",
    plate: "粤B·7P221",
    task: "车位区域识别",
    confidence: "96.4%",
    vehicleType: "商务车",
    location: "地下 C 区 08 车位",
    boxStyle: { left: "44%", top: "38%", width: "34%", height: "24%" },
    steps: [
      { label: "区域映射", value: "车位轮廓已匹配" },
      { label: "占用判断", value: "当前状态为占用" },
      { label: "结果同步", value: "待写入停车记录" },
    ],
  },
  {
    id: "exit",
    label: "出口识别",
    plate: "粤B·Q8M61",
    task: "出口结算识别",
    confidence: "97.3%",
    vehicleType: "SUV",
    location: "南出口 1 号道",
    boxStyle: { left: "22%", top: "50%", width: "28%", height: "13%" },
    steps: [
      { label: "目标追踪", value: "出口车辆已锁定" },
      { label: "车牌识别", value: "结果稳定输出" },
      { label: "离场结算", value: "待联动计费模块" },
    ],
  },
];
