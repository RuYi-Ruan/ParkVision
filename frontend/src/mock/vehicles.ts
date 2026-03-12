import type { Vehicle } from "./types";

// 车辆状态筛选项与页面按钮保持一致。
export const vehicleStatusFilters = [
  { label: "全部", value: "all" },
  { label: "已备案", value: "free" },
  { label: "停用", value: "warning" },
] as const;

export const vehicles: Vehicle[] = [
  { id: 1, plate: "粤B·A2138", owner: "张三", category: "新能源轿车", space: "固定车", status: "已备案", type: "free" },
  { id: 2, plate: "粤B·Q8M61", owner: "李四", category: "SUV", space: "月租车", status: "已备案", type: "free" },
  { id: 3, plate: "粤B·7P221", owner: "王五", category: "商务车", space: "企业车辆", status: "已备案", type: "free" },
  { id: 4, plate: "粤B·D9C12", owner: "赵六", category: "小型车", space: "临时车", status: "停用", type: "warning" },
];
